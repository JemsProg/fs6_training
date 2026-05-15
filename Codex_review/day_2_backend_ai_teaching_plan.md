# Day 2 Backend Teaching Plan: Django, DRF, PostgreSQL, and AI-Assisted API Development

## Class Context

**Class time:** 9:00 AM to 4:00 PM  
**Main goal:** Students learn how to build the backend foundation for the e-commerce app using Django, Django REST Framework, and PostgreSQL.  
**AI goal:** Students learn how to use AI to understand backend concepts, generate API drafts, debug errors, and review security risks without blindly trusting generated backend code.

Day 2 should connect directly to Day 1. On Day 1, students built the face of the store. On Day 2, they begin building the system behind the store: database models, API endpoints, authentication, and cart behavior.

The teaching focus should be clarity over feature overload. Students do not need to master every Django concept today. They need to understand the request-response flow:

```text
Frontend request -> Django URL -> DRF view -> Serializer -> Model/database -> JSON response
```

## Learning Outcomes

By the end of Day 2, students should be able to:

- Explain what Django is and why it is useful for backend development.
- Create or understand a Django project and app structure.
- Explain what Django REST Framework does.
- Create models for products and cart items.
- Connect Django to PostgreSQL.
- Build API endpoints for product list and product detail.
- Build beginner-level cart endpoints for add, update, and remove.
- Understand the basic flow of user registration and JWT login.
- Use AI to explain backend errors, review API structure, and generate test ideas.
- Identify backend code that is unsafe even if it appears to work.

## Recommended Schedule

### 9:00 AM - 9:30 AM: Recap And Backend Mindset

Start by connecting Day 1 to Day 2.

Discussion:

- Yesterday, the frontend displayed products.
- Today, the backend will provide those products.
- The frontend should not permanently depend on hardcoded product data.
- A real app stores data in a database and exposes it through APIs.

Simple explanation:

```text
React is the customer-facing side.
Django is the kitchen and storage room.
PostgreSQL is where the actual data lives.
DRF is the waiter that serves data as JSON.
```

AI adoption moment:

Ask AI:

```text
Explain Django, Django REST Framework, and PostgreSQL to a beginner using an online store as the example.
```

Class activity:

- Ask students which part of the AI explanation was useful.
- Ask which part sounded too advanced.
- Rewrite the explanation together in simpler terms.

Teaching point:

AI can explain concepts in many ways. Students should learn to ask for simpler, shorter, or more example-based explanations.

## 9:30 AM - 10:15 AM: Django Project Structure

Teach the structure before writing too much code.

Core concepts:

- Django project vs Django app.
- `manage.py`
- `settings.py`
- `urls.py`
- `models.py`
- `views.py`
- `serializers.py`
- `admin.py`
- `migrations/`

Use the existing project shape as the reference:

```text
backend/
  manage.py
  backend/
    settings.py
    urls.py
  base/
    models.py
    views.py
    serializers.py
    urls.py
```

Explain:

- The inner `backend/` folder is the project configuration.
- The `base/` folder is the app where business logic lives.
- `models.py` defines database tables.
- `serializers.py` converts model data to JSON and validates input.
- `views.py` contains API logic.
- `urls.py` maps routes to views.

Mini activity:

Students draw this flow:

```text
/products/ -> urls.py -> product_list view -> Product model -> ProductSerializer -> JSON
```

AI adoption moment:

Students ask AI:

```text
Explain the difference between a Django project and a Django app in one paragraph, then give me a simple folder example.
```

## 10:15 AM - 10:30 AM: Break

Quick check:

- Can students explain what `models.py` is for?
- Can students explain what `urls.py` is for?
- Can students explain why APIs return JSON?

## 10:30 AM - 11:15 AM: PostgreSQL And Models

Teach models as database table blueprints.

Core concepts:

- A model becomes a database table.
- A model field becomes a database column.
- Django migrations update the database structure.
- PostgreSQL stores the real data.

Recommended models for class:

```python
class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=255)
    description = models.TextField()
    countInStock = models.IntegerField()
    image = models.ImageField(upload_to="product_images/")
    createdAt = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product_name
```

For teaching, explain every field:

- `CharField` for short text.
- `TextField` for longer descriptions.
- `DecimalField` for prices.
- `IntegerField` for stock.
- `ImageField` for product images.
- `auto_now_add=True` for created date.

PostgreSQL teaching notes:

- Use local PostgreSQL if students are ready.
- If setup time is limited, show PostgreSQL configuration and let students run SQLite temporarily.
- Make it clear that SQLite is okay for local practice, while PostgreSQL is closer to deployment.

Recommended `settings.py` lesson:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "your_database_name",
        "USER": "your_database_user",
        "PASSWORD": "your_database_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

Important security note:

Tell students this is the simple classroom version. In real projects, database credentials should come from environment variables, not direct source code.

AI adoption moment:

Students ask AI:

```text
Explain this Django Product model field by field. Also tell me which fields need validation in a real e-commerce app.
```

## 11:15 AM - 12:00 PM: Django REST Framework And Serializers

Teach serializers as translators.

Simple explanation:

```text
Django model object -> serializer -> JSON for frontend
JSON from frontend -> serializer -> validated Python data
```

Install/setup concepts:

- `rest_framework` in `INSTALLED_APPS`
- `serializers.ModelSerializer`
- `fields = "__all__"`

Example:

```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
```

Teach this carefully:

- `ProductSerializer` is connected to `Product`.
- `fields = "__all__"` exposes every model field.
- In beginner lessons this is convenient.
- In real projects, be intentional about which fields are exposed.

AI adoption moment:

Students ask AI:

```text
Explain what a Django REST Framework serializer does using a Product API example.
```

Then ask:

```text
What is the risk of using fields = "__all__" in a production API?
```

Teaching point:

AI should not only generate code. It should help students ask, "What can go wrong?"

## 12:00 PM - 1:00 PM: Lunch

Optional lunch reflection:

Students write one sentence for each:

- Model
- Serializer
- View
- URL
- API endpoint

## 1:00 PM - 1:45 PM: Product API Endpoints

Build the simplest useful APIs first.

Endpoints:

```text
GET /products/
GET /products/<id>/
```

Example views:

```python
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

@api_view(["GET"])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)
```

Example URLs:

```python
from django.urls import path
from .views import product_list, product_detail

urlpatterns = [
    path("products/", product_list, name="product_list"),
    path("products/<int:pk>/", product_detail, name="product_detail"),
]
```

Teach:

- `many=True` means many objects.
- `get_object_or_404` is safer than manually querying and crashing.
- `Response(serializer.data)` sends JSON.

Hands-on:

- Students create product list and product detail endpoints.
- Test using browser, Postman, Thunder Client, or REST Client.

AI adoption moment:

Students ask AI:

```text
Review this DRF product list and detail API. Tell me if it is beginner-friendly and what could be improved later.
```

## 1:45 PM - 2:30 PM: User Registration And Login

Teach the minimum auth flow needed for the e-commerce app.

Core concepts:

- Django has a built-in `User` model.
- Registration creates a user.
- Login verifies username and password.
- JWT gives the frontend a token.
- Protected endpoints require a valid token.

Registration serializer example:

```python
from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
```

Registration view:

```python
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["POST"])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

JWT routes:

```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
```

Teach:

- Never store plain text passwords.
- `create_user()` hashes the password.
- JWT access tokens are short-lived.
- Refresh tokens are used to request new access tokens.

AI adoption moment:

Students ask AI:

```text
Explain access tokens and refresh tokens to a beginner. Use a school ID analogy.
```

Security warning:

This is a good time to say clearly: authentication code is not something students should blindly copy from AI. It must be tested.

## 2:30 PM - 2:45 PM: Break

Quick check:

- Can students register a user?
- Can students log in and receive tokens?
- Can students explain why passwords need hashing?

## 2:45 PM - 3:30 PM: Cart API Endpoints

Teach cart as the first user-owned resource.

Core concepts:

- Cart items belong to a user.
- Cart items belong to a product.
- Protected endpoints require login.
- Users should only see and change their own cart items.

Recommended cart model:

```python
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qty = models.IntegerField()
    createdAt = models.DateField(auto_now_add=True)
```

Recommended endpoints:

```text
GET /cart/
POST /cart/add/
PUT /cart/update/<id>/
DELETE /cart/delete/<id>/
```

Teach this rule:

Every cart query must filter by `request.user`.

Good:

```python
cart_items = CartItem.objects.filter(user=request.user)
```

Dangerous:

```python
cart_items = CartItem.objects.all()
```

Important validation:

- Quantity should be greater than zero.
- User should not update another user's cart item.
- Product must exist.
- Backend should eventually check stock.

AI adoption moment:

Students ask AI:

```text
Review this cart API for security. Can one user access another user's cart? What should I check?
```

Teaching point:

AI is very useful for security review prompts, but students must verify the code themselves.

## 3:30 PM - 3:50 PM: Connect Backend Concepts To Frontend

Show how Day 1 frontend connects to Day 2 backend.

Example frontend requests:

```js
axios.get(`${BASE_URL}/products/`)
axios.get(`${BASE_URL}/products/1/`)
axios.post(`${BASE_URL}/cart/add/`, payload, {
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
})
```

Explain:

- Public endpoints do not need a token.
- Cart endpoints need a token.
- Frontend should handle loading, success, and error states.
- Backend errors should be shown clearly to users.

AI adoption moment:

Students ask AI:

```text
Given these Django API endpoints, show me how a React frontend would call them with axios. Keep it beginner-friendly.
```

Instructor warning:

AI may generate a full frontend page. Tell students to only extract the request logic they understand.

## 3:50 PM - 4:00 PM: Wrap-Up And Reflection

End with a clear summary.

Students should answer:

- What is a model?
- What is a serializer?
- What is a view?
- What is an API endpoint?
- Why does the cart need authentication?
- What did AI help explain today?
- What AI answer did they need to question or verify?

Exit ticket:

Students submit:

- Screenshot of product list API response.
- Screenshot of product detail API response.
- Screenshot of successful login token response.
- Screenshot or note showing one cart endpoint test.
- One AI prompt they used.
- One backend security rule they learned.

## Recommended Instructor Flow

Use this rhythm:

1. Draw the request flow.
2. Show the code.
3. Run the endpoint.
4. Show the JSON response.
5. Break the code intentionally.
6. Use the error message to debug.
7. Ask AI to explain the error.
8. Fix the issue manually.

This teaches students not to fear backend errors.

## Assessment Rubric

### Beginner Passing Output

The student has:

- Django project/app running.
- Product model created.
- Product serializer created.
- Product list endpoint working.
- Product detail endpoint working.
- Registration endpoint attempted or working.
- JWT login endpoint working.
- Basic cart model or cart endpoint structure started.

### Strong Output

The student also has:

- PostgreSQL connected successfully.
- Cart endpoints filter by logged-in user.
- Cart add/update/delete works through API testing tool.
- Registration hashes passwords using `create_user()`.
- Protected endpoints use `IsAuthenticated`.
- Student can explain the flow without reading AI's answer.

### Needs Improvement

The student may need help if:

- They do not understand the difference between model, serializer, and view.
- They copied AI code with imports that do not exist.
- Their cart endpoint exposes all users' carts.
- They hardcoded secrets without understanding the risk.
- They cannot explain what JWT tokens are for.
- They only know that the API works but not how the request reaches the view.

## AI Rules For Day 2

Backend AI rules should be stricter than frontend AI rules because backend mistakes can affect data and security.

Allowed AI use:

- Explain Django errors.
- Explain models, serializers, views, and URLs.
- Generate draft serializers or views.
- Suggest tests.
- Review endpoint security.
- Explain database connection errors.

Not allowed without review:

- Copying full authentication code without explanation.
- Copying payment or security logic blindly.
- Accepting database settings with real credentials in source code.
- Using packages that were not discussed in class.
- Applying migrations without understanding what changed.

Required student habit:

Before keeping AI-generated backend code, students must answer:

```text
What input does this code receive?
What database table does it touch?
What output does it return?
What can go wrong?
Can another user access data they should not access?
```

## Suggested Homework

Students should finish or improve:

- Product list endpoint.
- Product detail endpoint.
- Register endpoint.
- JWT login test.
- Cart add endpoint.
- Cart list endpoint.

AI homework rule:

Students may use AI, but they must include a short note:

- What prompt they used.
- What code AI suggested.
- What they accepted.
- What they changed.
- What they rejected and why.

Optional challenge:

- Add validation so cart quantity cannot be less than 1.
- Add product stock checking.
- Add a `/profile/` endpoint that returns the logged-in user's username and email.
- Add API documentation in Markdown.

## Instructor Notes For Your Existing Project

Your current project already contains many Day 2 concepts:

- Product list and detail endpoints in `backend/base/views.py`
- Product, cart, payment, order, and shipping models in `backend/base/models.py`
- DRF serializers in `backend/base/serializers.py`
- JWT routes in `backend/base/urls.py`
- Cart ownership filtering using `request.user`

Use it as a reference, but be careful not to show everything at once. Payment, shipping, and webhook logic are too much for Day 2 unless students are already advanced.

Recommended Day 2 boundary:

- Teach products.
- Teach registration/login.
- Teach cart basics.
- Mention checkout only as a future feature.

The best closing line for students:

> Yesterday we built the store's face. Today we built the store's memory and rules. Tomorrow, we connect them more deeply and make the app feel real.
