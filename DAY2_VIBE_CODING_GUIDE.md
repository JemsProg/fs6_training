# Day 2 — Vibe Coding Guide
## Auth + Cart Views | Project-Context Prompting

> **How this works:** You give the AI your actual project files + coding rules first, then send a short task. The AI writes code that fits your project — not generic boilerplate.

---

## The Project Context Block
### Paste this ONCE at the start of every session. Never skip this step.

```
You are helping me build a Django REST Framework backend for an e-commerce app.

Here are the project files you need to understand before writing any code.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE: base/models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=255)
    description = models.TextField()
    countInStock = models.IntegerField()
    image = models.ImageField(upload_to='products_images/')
    createdAt = models.DateField(auto_now_add=True)

class cartUser(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qty = models.IntegerField()
    createdAt = models.DateField(auto_now_add=True)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE: base/serializers.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import Product, cartUser

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    class Meta:
        model = cartUser
        fields = ['id', 'product', 'product_id', 'qty']

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE: base/urls.py (already set up — do not change)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
path('register/',               register_user)
path('api/token/',              TokenObtainPairView.as_view())
path('api/token/refresh/',      TokenRefreshView.as_view())
path('logout/',                 logout_user)
path('profile/',                profile_view)
path('cart/',                   cart_view)
path('cart/add/',               add_to_cart)
path('cart/update/<int:pk>/',   update_cart_item)
path('cart/delete/<int:pk>/',   delete_cart_item)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXISTING VIEWS (already done — use these as pattern reference)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_product_data(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJECT CODING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Always use @api_view and Response — never class-based views
- Protected routes always have @permission_classes([IsAuthenticated])
- Cart and order queries always filter by request.user — never .all()
- Use get_object_or_404(Model, pk=pk, user=request.user) for user-owned records
- Status codes: 201 for created, 200 for ok, 204 for deleted, 400 for bad input, 205 for logout
- Never return raw model objects — always go through a serializer
- Write only the view function and its required imports — nothing else
```

---

## Task 1 — `register_user`

After pasting the context block, send this:

```
Using the project context above, write the register_user view.

Requirements:
- POST /register/ — no auth needed
- Validate incoming data using RegisterSerializer
- On success: save the user, return {"message": "User registered successfully"} with status 201
- On failure: return serializer.errors with status 400
- Include only the imports needed for this view
```

---

**If the output looks wrong, send this correction prompt:**

```
The register_user view is almost right. Fix these issues:
- [describe the specific problem here]
- Keep everything else exactly the same
- Do not rewrite the serializer
```

---

## Task 2 — `logout_user`

```
Using the project context above, write the logout_user view.

Requirements:
- POST /logout/ — no auth needed
- Expects {"refresh": "<token>"} in request body
- If refresh token is missing: return {"error": "Refresh token is required"} with status 400
- Parse the token using RefreshToken from rest_framework_simplejwt.tokens
- If the token has a blacklist method, call it
- If the token is invalid (TokenError): return {"error": "Invalid token"} with status 400
- On success: return {"message": "User logged out successfully"} with status 205
- Include only the imports needed for this view
```

---

## Task 3 — `profile_view`

```
Using the project context above, write the profile_view view.

Requirements:
- GET /profile/ — requires authentication
- Serialize the currently logged-in user using UserSerializer
- Return the serialized user data
- Include only the imports needed for this view
```

---

## Task 4 — `cart_view`

```
Using the project context above, write the cart_view view.

Requirements:
- GET /cart/ — requires authentication
- Get only the cart items that belong to request.user — never return all cart items
- Serialize using CartItemSerializer with many=True
- Return the serialized list
- Include only the imports needed for this view
```

---

## Task 5 — `add_to_cart`

```
Using the project context above, write the add_to_cart view.

Requirements:
- POST /cart/add/ — requires authentication
- Validate incoming data using CartItemSerializer
- On invalid: return serializer.errors with status 400
- After validation, extract product and qty from serializer.validated_data
- Use get_or_create to either find an existing cart item (same user + product) or create a new one
  - Use defaults={'qty': qty} so qty only applies on create
- If the item already existed (not created): add the new qty to the existing qty and save
- Serialize the final cart_item using CartItemSerializer for the response
- Return status 201 if the item was newly created, 200 if it already existed
- Include only the imports needed for this view
```

---

**If the AI skips the two-serializer pattern, send this:**

```
In add_to_cart, you need two separate serializer instances:
1. CartItemSerializer(data=request.data) — to validate the incoming request
2. CartItemSerializer(cart_item) — to serialize the saved cart_item for the response

Update the view to use two serializer instances. Do not change anything else.
```

---

## Task 6 — `update_cart_item`

```
Using the project context above, write the update_cart_item view.

Requirements:
- PUT /cart/update/<int:pk>/ — requires authentication
- Fetch the cart item using get_object_or_404 — filter by BOTH pk and request.user
- Serialize with CartItemSerializer using partial=True so only qty needs to be sent
- On valid: save and return serializer.data
- On invalid: return serializer.errors with status 400
- Include only the imports needed for this view
```

---

## Task 7 — `delete_cart_item`

```
Using the project context above, write the delete_cart_item view.

Requirements:
- DELETE /cart/delete/<int:pk>/ — requires authentication
- Fetch the cart item using get_object_or_404 — filter by BOTH pk and request.user
- Delete the item
- Return an empty response with status 204
- Include only the imports needed for this view
```

---

## Combining All Views Into One Prompt

If you want the AI to write all 7 views in one shot, send this after the context block:

```
Using the project context above, write all 7 views in this exact order:
1. register_user — POST /register/, uses RegisterSerializer, no auth, returns 201/400
2. logout_user — POST /logout/, blacklists refresh token, returns 205/400
3. profile_view — GET /profile/, IsAuthenticated, uses UserSerializer
4. cart_view — GET /cart/, IsAuthenticated, filter by request.user, CartItemSerializer many=True
5. add_to_cart — POST /cart/add/, IsAuthenticated, get_or_create with defaults, two serializer instances, 201 if new / 200 if updated
6. update_cart_item — PUT /cart/update/<pk>/, IsAuthenticated, get_object_or_404 with user, partial=True
7. delete_cart_item — DELETE /cart/delete/<pk>/, IsAuthenticated, get_object_or_404 with user, 204 no body

Write all views in one file block. Include all imports at the top. Follow the coding rules from the context. Do not include any serializer or model definitions.
```

---

## Debugging Prompts

When the AI generates something broken, use these focused correction prompts:

**Wrong status code:**
```
In [view name], change the success status code from [wrong] to [correct]. Do not change anything else.
```

**Missing user isolation:**
```
In [view name], the query is using .all() — fix it to filter by request.user only. Do not change anything else.
```

**Missing partial=True:**
```
In update_cart_item, the serializer is not using partial=True. Add it. The serializer line should be:
serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
Do not change anything else.
```

**AI rewrote the serializer:**
```
Do not touch the serializer classes. I only want the view function rewritten. Here is what the view should do: [describe again].
```

**AI used class-based views:**
```
This project only uses function-based views with @api_view. Rewrite [view name] as a function-based view. Do not use APIView or ViewSets.
```

---

## Iteration Prompts (After Views Are Working)

Use these to extend what was built today:

```
Using the project context above, add a new endpoint: GET /cart/count/ that returns the total number of items in the logged-in user's cart as {"count": <number>}. Follow all the same coding rules.
```

```
Using the project context above, update add_to_cart so that if the qty would exceed 10 for a single product, it returns {"error": "Maximum quantity per product is 10"} with status 400.
```

```
Using the project context above, update delete_cart_item so that after deleting, it returns the updated full cart list instead of a 204. Use cart_view's logic as a reference.
```
