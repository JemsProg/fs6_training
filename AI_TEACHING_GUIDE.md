# AI Teaching Guide — fs6_training Django REST Backend

This guide gives you ready-to-paste AI prompts to teach every layer of this backend. Each section includes the **AI context block** (paste this first) and the **teaching prompts** you send after. The context primes the AI with exact project knowledge so answers are specific, not generic.

---

## How to Use This Guide

1. Open any AI chat (Claude, ChatGPT, Gemini, etc.)
2. Paste the **Context Block** at the start of your session
3. Then send any of the **Teaching Prompts** below
4. Follow up with your own questions — the AI now knows your exact project

---

## Master Context Block

Paste this once at the start of any AI session before asking teaching questions:

```
PROJECT CONTEXT — fs6_training Django Backend

Stack: Django 5.0.6, Django REST Framework 3.16.1, JWT auth (simplejwt), PostgreSQL (production), SQLite (dev), PayMongo payment gateway, CORS enabled.

MODELS:
- Product: product_name, product_price, brand, description, countInStock, image, createdAt
- cartUser: product (FK→Product), user (FK→User), qty, createdAt
- paymentMethod: user (FK→User), totalPrice, isPaid, paidAt, paymongopayment, paymongostatus | method mark_paid() creates OrderItems from cart, clears cart, sets isPaid=True (atomic)
- orderItem: product (FK→Product), payment (FK→paymentMethod), qty, price
- shippingAddress: paymentId (FK→paymentMethod), fullName, address, city, postalCode, country

SERIALIZERS: RegisterSerializer (validates unique email, hashes password), UserSerializer, ProductSerializer, CartItemSerializer (nested product), ShippingAddressSerializer, OrderItemSerializer (has computed line_total), PaymentMethodSerializer (nested items + shipping), CheckoutSerializer (input validation only)

API ENDPOINTS:
  Public: GET /products/, GET /products/<id>/, POST /register/, POST /api/token/, POST /api/token/refresh/
  Protected (JWT Bearer): GET /profile/, GET /cart/, POST /cart/add/, PUT /cart/update/<id>/, DELETE /cart/delete/<id>/, POST /checkout/gcash/, GET /orders/
  Webhook (csrf_exempt): POST /webhook/paymongo/

AUTH FLOW: JWT tokens — login at /api/token/, include access token as Authorization: Bearer <token>, refresh at /api/token/refresh/, logout blacklists refresh token.

PAYMENT FLOW: POST /checkout/gcash/ → validates shipping (CheckoutSerializer) → recalculates total server-side from cart (never trusts frontend) → calls PayMongo API (links endpoint, Basic Auth with base64-encoded secret) → saves paymentMethod (isPaid=False) + shippingAddress → returns checkout_url. PayMongo webhook hits /webhook/paymongo/ on payment, triggers mark_paid() atomically.

KEY PATTERNS: user isolation on all cart/order queries (filter by request.user), atomic transactions (checkout + mark_paid), idempotent webhook handling, prefetch_related for order queries, @csrf_exempt on webhook only.

DEPLOYMENT: Gunicorn WSGI, Railway PostgreSQL, Vercel frontend at https://fs6-training-git-main-jemsprogs-projects.vercel.app, CORS allows localhost:5173 and the Vercel domain.
```

---

## Module 1 — Django Project Structure

**Goal:** Understand how the files and folders connect.

```
Using the project context above, explain the purpose of each file in this Django project:
backend/settings.py, backend/urls.py, base/models.py, base/views.py, base/serializers.py, base/urls.py, manage.py, requirements.txt.

Explain how a request flows from the browser all the way to the database and back. Use the GET /products/ endpoint as the example.
```

```
Why does this project have two folders — `backend/` and `base/`? What is the difference between a Django project and a Django app? When would you add a second app?
```

---

## Module 2 — Models & Database

**Goal:** Understand ORM models, relationships, and migrations.

```
Using the project context above, walk me through the 5 models: Product, cartUser, paymentMethod, orderItem, shippingAddress.

For each model explain:
1. What real-world thing it represents
2. What each field does
3. Which fields are ForeignKeys and what relationship they create (one-to-many, etc.)

Then draw the relationships as a simple text diagram.
```

```
The mark_paid() method on paymentMethod is critical. Using the context above, explain step by step what it does, why it's wrapped in an atomic transaction, and what would go wrong if it wasn't atomic.
```

```
What is a Django migration? Walk me through the commands I'd run to add a new field `product_category` (CharField) to the Product model and apply it to the database.
```

```
The cartUser model uses two ForeignKeys: product and user. Explain what CASCADE means on a ForeignKey delete. What happens to a user's cart items if their account is deleted? What happens to cart items if the product is deleted?
```

---

## Module 3 — Serializers

**Goal:** Understand DRF serializers — validation, transformation, nesting.

```
Using the project context above, explain what Django REST Framework serializers do. Why can't we just send a model object directly to the browser?

Then explain the difference between these serializer types used in this project:
- ModelSerializer vs plain Serializer (CheckoutSerializer)
- Read-only fields vs write-only fields (see CartItemSerializer: product is read-only, product_id is write-only)
- Nested serializers (CartItemSerializer has a nested ProductSerializer)
```

```
Walk me through RegisterSerializer. It validates a unique email and hashes the password. Show me:
1. How the validate_email method works
2. Why we use create_user() instead of User() directly
3. What would happen if we forgot to hash the password
```

```
OrderItemSerializer has a computed field line_total that multiplies qty × price. Explain how SerializerMethodField works and when you'd use it instead of a model property.
```

---

## Module 4 — Views & API Design

**Goal:** Understand function-based views, decorators, permissions, and REST conventions.

```
Using the project context above, explain how a Django REST Framework function-based view works. Use the cart_view() endpoint as the example. Cover:
1. The @api_view(['GET']) decorator
2. The @permission_classes([IsAuthenticated]) decorator
3. How request.user works with JWT authentication
4. How filtering by request.user provides user isolation
```

```
Compare the add_to_cart and update_cart_item views. One uses POST and one uses PUT. Explain:
1. When to use GET, POST, PUT, PATCH, DELETE in REST APIs
2. Why add_to_cart creates OR updates (get_or_create pattern)
3. What status codes 200, 201, 204, 400, 404 mean and which views use each
```

```
The create_gcash_payment view is the most complex. Walk through it step by step:
1. Why does it recalculate the total from the cart instead of accepting a total from the frontend?
2. How does it call the PayMongo API (what is Basic Auth, base64 encoding, why multiply by 100)?
3. What data does it save to the database before the user actually pays?
4. What does it return to the frontend and why?
```

```
The paymongo_webhook view has @csrf_exempt. What is CSRF protection and why is it normally needed? Why is it safe to disable it specifically for this webhook endpoint?
```

---

## Module 5 — Authentication & JWT

**Goal:** Understand JWT tokens, login flow, and protecting endpoints.

```
Using the project context above, explain the full authentication flow from registration to a protected API call:

1. POST /register/ — what happens server-side?
2. POST /api/token/ — what are the access and refresh tokens? What is inside a JWT?
3. How does the frontend include the token in a request? (Authorization header format)
4. How does @permission_classes([IsAuthenticated]) validate the token?
5. POST /api/token/refresh/ — why do access tokens expire and why is a refresh token needed?
6. POST /logout/ — what does "blacklisting" a refresh token mean?
```

```
What is the difference between authentication and authorization? Give an example of each using endpoints from this project.
```

```
If a user sends a request to GET /cart/ without a token, what HTTP status code does Django return and why? What if the token is expired?
```

---

## Module 6 — URL Routing

**Goal:** Understand how Django routes URLs to views.

```
Using the project context, trace how a request to POST /checkout/gcash/ gets routed to the create_gcash_payment function. Start from backend/urls.py → base/urls.py → the view. Explain what include() does and why splitting URLs across files is good practice.
```

```
Some URL patterns have <int:pk> in them (e.g., /cart/update/<int:pk>/). Explain:
1. What is a URL parameter / path converter?
2. Why <int:pk> instead of just <pk>?
3. How does the view function receive this value?
```

---

## Module 7 — CORS & Middleware

**Goal:** Understand CORS, middleware stack, and why it matters for frontend-backend communication.

```
Using the project context, explain CORS (Cross-Origin Resource Sharing):
1. Why does a React frontend at localhost:5173 need CORS headers to call a Django backend at localhost:8000?
2. What does the django-cors-headers package do?
3. Why are the specific origins listed (localhost:5173, localhost:5174, the Vercel URL)?
4. What would happen if CORS was not configured and the frontend tried to make an API call?
```

```
Explain what Django middleware is. Walk through the middleware stack in this project in order. What does each middleware do and why does the order matter (especially CorsMiddleware being first)?
```

---

## Module 8 — Database Queries & Optimization

**Goal:** Understand ORM queries, filtering, and the N+1 problem.

```
Using the project context, explain these ORM query patterns used in the views:

1. cartUser.objects.filter(user=request.user) — why filter by user?
2. paymentMethod.objects.filter(user=request.user).order_by('-id') — what does order_by('-id') do?
3. .prefetch_related('orderitem_set', 'shippingaddress_set') — what is prefetch_related and what problem does it solve?
4. get_object_or_404(cartUser, pk=pk, user=request.user) — why include user=request.user in the lookup?
```

```
What is the N+1 query problem? Give a concrete example using the orders list endpoint (GET /orders/) where it would occur WITHOUT prefetch_related, then explain how prefetch_related fixes it.
```

---

## Module 9 — Payment Integration (PayMongo)

**Goal:** Understand third-party API integration and webhook patterns.

```
Using the project context, explain the complete GCash payment lifecycle from "user clicks checkout" to "order is confirmed":

1. Frontend sends POST /checkout/gcash/ with shipping details
2. Backend creates a PayMongo payment link (explain the API call, Basic Auth, amount in centavos)
3. Database state at this point: what is saved, what is isPaid?
4. User is redirected to checkout_url — what happens on PayMongo's side?
5. PayMongo calls POST /webhook/paymongo/ when paid
6. Webhook calls mark_paid() — what changes in the database?
7. What does the user see when they return?
```

```
Why is the webhook endpoint idempotent? What would happen if PayMongo sends the same webhook twice (duplicate delivery)? How does this project handle it?
```

```
The PayMongo secret key is hardcoded in views.py. This is a security risk. Explain:
1. Why is a hardcoded API key dangerous?
2. How would you move it to an environment variable using os.environ or django-environ?
3. How would Railway and Vercel handle this in production?
```

---

## Module 10 — Security & Production Readiness

**Goal:** Identify security issues and understand production best practices.

```
Review this project's settings.py for security issues. The known problems are:
- SECRET_KEY is hardcoded
- DEBUG = True
- ALLOWED_HOSTS = ['*']
- PostgreSQL credentials hardcoded
- PayMongo API key hardcoded in views.py

For each issue, explain:
1. What the risk is (what can an attacker do?)
2. How to fix it using environment variables
3. How Django's settings work differently in development vs production
```

```
This project uses SQLite in development and PostgreSQL in production (Railway). Explain:
1. Why not use PostgreSQL in development too?
2. What is DATABASE_URL and how does dj-database-url work?
3. What is a database migration and why must you run it on the production database after deploying?
```

---

## Module 11 — Putting It All Together (Full Request Trace)

**Goal:** Connect all layers for a complete end-to-end understanding.

```
Using the project context, trace a complete user journey from zero to completed order. For each step, name the exact endpoint, which view function handles it, which serializer validates data, which models are read or written, and what is returned:

1. User registers an account
2. User logs in and gets a JWT token
3. User views the product list
4. User adds a product to their cart
5. User views their cart
6. User goes to checkout (GCash)
7. User pays on PayMongo
8. PayMongo fires the webhook
9. User views their order history
```

---

## Module 12 — Exercises & Challenges

Use these prompts to generate coding exercises for a student:

```
Using the project context above, create 5 progressive coding exercises for a student learning Django REST Framework. Start from easy (read-only endpoint) and end at hard (authenticated write with validation). For each exercise, specify exactly which files to modify and what the expected API behavior should be.
```

```
The tests.py file in base/ is empty. Using the project context, write test cases for:
1. The register endpoint (success, duplicate email, missing fields)
2. The cart add endpoint (authenticated success, unauthenticated 401, product not found 404)
3. The checkout endpoint (valid cart, empty cart edge case)

Use Django REST Framework's APITestCase and JWT token helpers.
```

```
A student wants to add a product search feature: GET /products/?search=nike should return only products where product_name or brand contains "nike" (case-insensitive). Using the project context, explain step by step how to implement this using Django ORM's Q objects and query parameters from request.query_params.
```

---

## Quick Reference Cheat Sheet

Paste this shorter block for quick Q&A when you don't need deep context:

```
QUICK REF — fs6_training backend (Django REST + JWT + PayMongo)
Endpoints: /products/ (public), /register/, /api/token/ (login), /api/token/refresh/, /logout/, /profile/, /cart/ (CRUD), /checkout/gcash/, /webhook/paymongo/, /orders/
Models: Product, cartUser, paymentMethod (has mark_paid()), orderItem, shippingAddress
Auth: JWT Bearer tokens, simplejwt, @permission_classes([IsAuthenticated])
Payment: PayMongo /v1/links, Basic Auth + base64, amount in centavos, webhook confirms payment
Key patterns: server-side total calculation, atomic transactions, user-isolated queries, idempotent webhook
```

---

## Tips for Better AI Teaching Sessions

- **Be specific** — instead of "explain serializers," ask "explain why CartItemSerializer uses product as read-only and product_id as write-only"
- **Ask for analogies** — "explain ForeignKey CASCADE using a real-world analogy"
- **Ask for contrast** — "what would break if we removed the atomic transaction from mark_paid()?"
- **Ask to show code** — "show me the exact query Django runs for prefetch_related on orders"
- **Ask to quiz you** — "ask me 5 questions about JWT authentication in this project and grade my answers"
