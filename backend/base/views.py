from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


# These decorator imports stay at the top because Python needs them before
# reading the view functions below.
# api_view tells Django REST Framework what HTTP method this function accepts.
# permission_classes is used when a route should only work for logged-in users.
# IsAuthenticated means the user must send a valid login token before entering.


from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
def product_list(request):
    # Get all products from the database.
    products = Product.objects.all()

    # many=True means we are converting many Product objects, not just one.
    # The serializer changes Python/Django objects into JSON-friendly data.
    serializer = ProductSerializer(products, many=True)

    # Response sends the JSON data back to the frontend.
    return Response(serializer.data)

from django.shortcuts import get_object_or_404
@api_view(['GET'])
def get_product_data(request, pk):
    # pk comes from the URL. Example: /products/3/ means pk is 3.
    # get_object_or_404 finds the product, or returns 404 if it does not exist.
    product = get_object_or_404(Product, pk=pk)

    # This time many=True is not needed because this is only one product.
    serializer = ProductSerializer(product)
    return Response(serializer.data)


#Register Function
from rest_framework import status
from .serializers import RegisterSerializer
@api_view(['POST'])
def register_user(request):
    # request.data contains the JSON sent by the frontend.
    # RegisterSerializer checks if username, email, and password are valid.
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        # save() calls the create() method inside RegisterSerializer.
        # In this project, that creates a new Django User.
        serializer.save()
        return Response(
            {'message': 'User registered successfully'},
            status=status.HTTP_201_CREATED,
        )

    # If validation fails, send the exact serializer errors to the frontend.
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Logout function
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
@api_view(['POST'])
def logout_user(request):
    # The frontend should send the refresh token in the request body.
    refresh_token = request.data.get('refresh')

    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # This checks if the refresh token is a real, valid JWT refresh token.
        token = RefreshToken(refresh_token)

        # Some projects enable SimpleJWT blacklist, and some do not.
        # If blacklist exists, we add the token there so it cannot be reused.
        if hasattr(token, 'blacklist'):
            token.blacklist()

    except TokenError:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {'message': 'User logged out successfully'},
        status=status.HTTP_205_RESET_CONTENT,
    )


#Profile View function
from .serializers import UserSerializer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    # request.user is the logged-in user.
    # DRF gets this user from the JWT token sent by the frontend.
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


#Cart Functions
from .models import cartUser
from .serializers import CartItemSerializer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    # Only get cart items owned by the logged-in user.
    # This prevents users from seeing another user's cart.
    cart_items = cartUser.objects.filter(user=request.user)
    serializer = CartItemSerializer(cart_items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    # CartItemSerializer validates product_id and qty from the frontend.
    serializer = CartItemSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # validated_data is safe to use because serializer.is_valid() already passed.
    # product is the actual Product object because product_id uses source='product'.
    product = serializer.validated_data['product']
    qty = serializer.validated_data['qty']

    # get_or_create checks if this product is already in the user's cart.
    # If it exists, created is False. If it is new, created is True.
    cart_item, created = cartUser.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'qty': qty},
    )

    if not created:
        # If the item is already in the cart, add the new quantity to the old one.
        cart_item.qty += qty
        cart_item.save()

    # Serialize the saved cart item so the frontend receives the latest data.
    output_serializer = CartItemSerializer(cart_item)
    response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response(output_serializer.data, status=response_status)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, pk):
    # Find the cart item by id, but only if it belongs to the logged-in user.
    cart_item = get_object_or_404(cartUser, pk=pk, user=request.user)

    # partial=True allows updating only one field, such as qty.
    serializer = CartItemSerializer(cart_item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cart_item(request, pk):
    # Again, filter by request.user so users can only delete their own cart item.
    cart_item = get_object_or_404(cartUser, pk=pk, user=request.user)
    cart_item.delete()

    # 204 means the delete worked, and there is no response body to send back.
    return Response(status=status.HTTP_204_NO_CONTENT)



# Checkout and Xendit Integration
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import transaction
import requests
from .models import paymentMethod, shippingAddress
from .serializers import CheckoutSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_xendit_payment(request):
    # CheckoutSerializer validates the shipping fields from the frontend.
    serializer = CheckoutSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Save these in variables so the rest of the function is easier to read.
    user = request.user
    data = serializer.validated_data

    if not user.email:
        return Response(
            {'error': 'Your account needs an email address before checkout.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Never trust the frontend total; compute the total from the cart.
    # select_related('product') also fetches product data in the same query.
    cart_items = cartUser.objects.filter(user=user).select_related('product')

    if not cart_items.exists():
        return Response(
            {'error': 'Cart is empty'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Add up each item's price times quantity to get the real order total.
    total_price = sum(
        item.product.product_price * item.qty
        for item in cart_items
    )

    if not settings.XENDIT_SECRET_KEY:
        # Do not continue without a secret key. A missing key should fail loudly
        # instead of creating a local order that can never be paid.
        return Response(
            {'error': 'XENDIT_SECRET_KEY is not configured'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Xendit hosted invoices use the currency amount, not PayMongo-style centavos.
    # Convert through Decimal first so we do not accidentally send floating errors.
    xendit_amount = float(Decimal(total_price).quantize(Decimal('0.01')))

    # external_id is our own unique reference. It lets us reconcile a webhook even
    # if the gateway invoice ID is not the easiest field to query in a callback.
    external_id = f'order-{user.id}-{uuid.uuid4().hex}'

    # Payload is the JSON body Xendit needs to create a hosted checkout page.
    # Only the backend creates this; the frontend never sees the secret key.
    payload = {
        'external_id': external_id,
        'amount': xendit_amount,
        'currency': 'PHP',
        'payer_email': user.email,
        'description': 'Order Payment',
        'success_redirect_url': settings.XENDIT_SUCCESS_REDIRECT_URL,
        'failure_redirect_url': settings.XENDIT_FAILURE_REDIRECT_URL,
        'customer': {
            'given_names': data['fullName'],
            'email': user.email,
        },
        'customer_notification_preference': {
            'invoice_created': ['email'],
            'invoice_paid': ['email'],
            'invoice_expired': ['email'],
        },
    }

    try:
        # Xendit uses HTTP Basic Auth where the API key is the username and the
        # password is blank. requests handles the base64 encoding for us.
        xendit_response = requests.post(
            'https://api.xendit.co/v2/invoices',
            auth=(settings.XENDIT_SECRET_KEY, ''),
            json=payload,
            timeout=30,
        )
        xendit_response.raise_for_status()

        # Convert Xendit's JSON response into a Python dictionary.
        result = xendit_response.json()
    except requests.RequestException as exc:
        # This catches network errors, timeout errors, or Xendit API errors.
        error_message = str(exc)
        if getattr(exc, 'response', None) is not None:
            try:
                error_message = exc.response.json()
            except ValueError:
                error_message = exc.response.text

        return Response(
            {'error': error_message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if 'invoice_url' not in result or 'id' not in result:
        # If Xendit did not return the fields we need, do not save a local order.
        return Response({'error': result}, status=status.HTTP_400_BAD_REQUEST)

    # Save important values from Xendit's response.
    checkout_url = result['invoice_url']
    xendit_invoice_id = result['id']
    xendit_status = result.get('status', 'PENDING')

    # transaction.atomic means both records must be saved together.
    # If one save fails, Django rolls back the other save too.
    with transaction.atomic():
        # Store the payment in our database while it is still unpaid.
        payment = paymentMethod.objects.create(
            user=user,
            totalPrice=total_price,
            isPaid=False,
            xendit_invoice_id=xendit_invoice_id,
            xendit_external_id=external_id,
            xendit_status=xendit_status,
        )

        # Store the shipping address connected to this payment.
        shippingAddress.objects.create(
            paymentId=payment,
            fullName=data['fullName'],
            address=data['address'],
            city=data['city'],
            postalCode=data['postalCode'],
            country=data['country'],
        )

    # Send the checkout link to the frontend so the user can pay on Xendit's page.
    return Response({'checkout_url': checkout_url}, status=status.HTTP_200_OK)


import json


@csrf_exempt
@api_view(['POST'])
def xendit_webhook(request):
    # A webhook is a request sent by Xendit to our backend.
    # csrf_exempt is used because Xendit is not a browser with a CSRF token.
    try:
        callback_token = request.headers.get('x-callback-token')

        if not settings.XENDIT_CALLBACK_TOKEN:
            # Production should always configure this value in the environment.
            # Without it, we cannot prove that the webhook came from Xendit.
            return Response(
                {'error': 'XENDIT_CALLBACK_TOKEN is not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if callback_token != settings.XENDIT_CALLBACK_TOKEN:
            # Never update orders from an unauthenticated webhook request.
            return Response(
                {'error': 'Invalid Xendit callback token'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # request.body is raw JSON bytes, so json.loads turns it into a dictionary.
        payload = json.loads(request.body)

        # Xendit invoice callbacks include both a gateway invoice ID and our
        # external_id. We try both so the handler is resilient to payload changes.
        xendit_invoice_id = payload.get('id')
        xendit_external_id = payload.get('external_id')
        xendit_status = payload.get('status')

        if not xendit_invoice_id and not xendit_external_id:
            return Response(
                {'error': 'Missing Xendit invoice reference'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find our payment record using the Xendit id or our own external id.
        payment = None
        if xendit_invoice_id:
            payment = paymentMethod.objects.filter(
                xendit_invoice_id=xendit_invoice_id,
            ).first()
        if not payment and xendit_external_id:
            payment = paymentMethod.objects.filter(
                xendit_external_id=xendit_external_id,
            ).first()

        if not payment:
            # This means Xendit sent an event, but our database has no match.
            return Response(
                {'message': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Keep the latest gateway status for support and reconciliation.
        if xendit_status:
            payment.xendit_status = xendit_status
            payment.save(update_fields=['xendit_status'])

        if xendit_status not in ['PAID', 'SETTLED']:
            # We only fulfill paid events. Other events are accepted after status
            # storage so Xendit does not keep retrying valid non-paid updates.
            return Response(
                {'message': 'Xendit event received'},
                status=status.HTTP_200_OK,
            )

        if payment.isPaid:
            # This prevents duplicate order items if Xendit sends the webhook twice.
            return Response(
                {'message': 'Already processed'},
                status=status.HTTP_200_OK,
            )

        # mark_paid updates the payment, creates order items, and clears the cart.
        payment.mark_paid()

        return Response(
            {'message': 'Payment confirmed. Order items created.'},
            status=status.HTTP_200_OK,
        )

    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        # If the webhook data is missing or invalid, return a clear bad request.
        return Response(
            {'error': str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )


from .serializers import PaymentMethodSerializer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_orders(request):
    # Get all payments/orders of the logged-in user, newest first.
    payments = (
        paymentMethod.objects
        .filter(user=request.user)
        .order_by('-id')
        # prefetch_related helps load related order items and shipping addresses faster.
        .prefetch_related('orderitem_set__product', 'shippingaddress_set')
    )

    # PaymentMethodSerializer also includes the order items and shipping details.
    serializer = PaymentMethodSerializer(payments, many=True)
    return Response(serializer.data)
