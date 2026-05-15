# Day 3 Teaching Plan: Connecting React To Django With REST APIs, JWT Auth, Cart, and Orders

## Class Context

**Class time:** 9:00 AM to 4:00 PM  
**Main goal:** Students connect the React frontend from Day 1 to the Django REST API from Day 2.  
**AI goal:** Students learn how to use AI to debug frontend-backend integration, understand API errors, review auth flow, and improve code without blindly copying large generated solutions.

Day 3 is where the app starts to feel real. Students move from static UI and isolated backend endpoints into a working fullstack flow:

```text
React page -> Axios request -> Django API -> Database -> JSON response -> React state update
```

The key teaching theme is integration. Many students can follow frontend lessons and backend lessons separately, but they struggle when the two sides meet. Today should slow down around the connection points: URLs, request bodies, response shapes, tokens, headers, CORS, loading states, and error handling.

## Learning Outcomes

By the end of Day 3, students should be able to:

- Connect React to Django REST Framework using Axios or `fetch`.
- Store a backend base URL in one reusable frontend file.
- Render products from the backend instead of hardcoded data.
- Register a user from the React frontend.
- Log in and store JWT access and refresh tokens.
- Send authenticated requests using the `Authorization: Bearer <token>` header.
- Protect pages such as profile, cart, and orders.
- Add products to cart from the frontend.
- Display the logged-in user's cart.
- View orders from the backend order endpoint.
- Use AI to debug request/response mismatches and explain API errors.
- Explain the full auth and cart flow in their own words.

## Recommended Schedule

### 9:00 AM - 9:30 AM: Recap And Fullstack Mental Model

Start with a visual recap.

Day 1:

```text
React components + Tailwind layout
```

Day 2:

```text
Django models + serializers + API endpoints
```

Day 3:

```text
React calls Django APIs and displays real data
```

Draw this on the board:

```text
Button click
  -> React function
  -> Axios request
  -> Django URL
  -> DRF view
  -> Serializer/model
  -> JSON response
  -> React state
  -> UI updates
```

AI adoption moment:

Ask AI:

```text
Explain how a React frontend connects to a Django REST API using an online store as the example.
```

Class discussion:

- What part of the explanation matches what students already know?
- What part is still unclear?
- What words should they watch for today? Examples: endpoint, token, header, payload, response, status code.

Teaching point:

Day 3 is not about memorizing code. It is about learning how data travels.

## 9:30 AM - 10:15 AM: Configure Frontend API Access

Teach students to avoid scattering backend URLs across many components.

Create or explain:

```text
src/api/base.js
```

Example:

```js
export const BASE_URL = "http://127.0.0.1:8000";
```

Then use it:

```js
import axios from "axios";
import { BASE_URL } from "../api/base";

const response = await axios.get(`${BASE_URL}/products/`);
```

Teach:

- The frontend and backend usually run on different ports.
- React dev server may be on `5173`.
- Django dev server may be on `8000`.
- CORS must be configured on the backend.
- A wrong URL creates connection errors or 404 errors.

Common errors to explain:

- `Network Error`: backend may not be running, URL may be wrong, or CORS may be blocking.
- `404 Not Found`: endpoint path is wrong.
- `500 Internal Server Error`: backend code crashed.
- `401 Unauthorized`: token is missing, invalid, or expired.
- `400 Bad Request`: request body does not match what the backend expects.

AI adoption moment:

Students ask AI:

```text
I am connecting React to Django and I got this error: [paste error]. Ask me for the URL, request body, and backend route before suggesting a fix.
```

Teaching point:

Students should train AI to ask diagnostic questions instead of guessing.

## 10:15 AM - 10:30 AM: Break

Quick check:

- Is Django running?
- Is React running?
- Does `BASE_URL` point to the backend?
- Can students call `/products/` from the browser?

## 10:30 AM - 11:15 AM: Load Products From Django

Replace hardcoded frontend products with backend data.

Recommended React flow:

```text
useState for products
useState for loading
useState for error
useEffect to fetch products
map products into ProductCard components
```

Example:

```jsx
import { useEffect, useState } from "react";
import axios from "axios";
import { BASE_URL } from "../api/base";

function ProductSection() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get(`${BASE_URL}/products/`);
        setProducts(response.data);
      } catch (err) {
        setError("Failed to load products.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (isLoading) return <p>Loading products...</p>;
  if (error) return <p>{error}</p>;

  return (
    <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </section>
  );
}

export default ProductSection;
```

Teach:

- `useEffect` runs after the component appears.
- `async/await` helps read API code clearly.
- `response.data` is the JSON returned by Django.
- Loading and error states are part of professional frontend work.

Important project-specific warning:

In the current project, the product detail route should be consistent. If the app route is `/products/:id`, product links should use `/products/${product.id}`.

AI adoption moment:

Students ask AI:

```text
Review this React API-fetching component. Check loading state, error state, dependency array, and whether the API response shape is used correctly.
```

## 11:15 AM - 12:00 PM: Register From React

Build the registration flow before login.

Endpoint:

```text
POST /register/
```

Expected request body:

```json
{
  "username": "student1",
  "email": "student1@example.com",
  "password": "password123"
}
```

Recommended frontend state:

```js
const [form, setForm] = useState({
  username: "",
  email: "",
  password: "",
});
```

Example submit logic:

```js
const handleRegister = async (e) => {
  e.preventDefault();

  try {
    await axios.post(`${BASE_URL}/register/`, form);
    navigate("/login");
  } catch (error) {
    console.error(error.response?.data || error.message);
  }
};
```

Teach:

- Form state stores what the user types.
- The frontend field names must match the backend serializer fields.
- Backend validation errors should be shown on the page.
- A successful register should usually redirect to login.

AI adoption moment:

Students ask AI:

```text
My Django register endpoint returns this error: [paste response]. Explain which frontend field or backend serializer rule is causing it.
```

Teaching point:

Good fullstack debugging compares the request body with the serializer.

## 12:00 PM - 1:00 PM: Lunch

Optional lunch task:

Students test registration with:

- Empty form
- Duplicate email or username
- Valid new user

They should observe how backend validation responds.

## 1:00 PM - 1:50 PM: Login And JWT Token Storage

Teach login as an exchange:

```text
username/password -> backend verifies -> backend returns tokens -> frontend stores tokens
```

Endpoint:

```text
POST /api/token/
```

Expected request body:

```json
{
  "username": "student1",
  "password": "password123"
}
```

Expected response:

```json
{
  "refresh": "...",
  "access": "..."
}
```

Example login logic:

```js
const handleLogin = async (e) => {
  e.preventDefault();

  try {
    const response = await axios.post(`${BASE_URL}/api/token/`, {
      username: form.username,
      password: form.password,
    });

    localStorage.setItem("access_token", response.data.access);
    localStorage.setItem("refresh_token", response.data.refresh);
    navigate("/profile");
  } catch (error) {
    console.error(error.response?.data || error.message);
  }
};
```

Important teaching correction:

Do not call an async login function and then immediately check `localStorage`. Navigate after the login request succeeds.

Good:

```js
const response = await axios.post(...);
localStorage.setItem(...);
navigate("/profile");
```

Risky:

```js
handleLogin();
if (localStorage.getItem("access_token")) {
  navigate("/profile");
}
```

Teach:

- The access token proves the user is logged in.
- The refresh token can request a new access token.
- `localStorage` is simple for class, but not perfect security.
- Token storage should be discussed honestly.

AI adoption moment:

Students ask AI:

```text
Explain this JWT login function line by line. Also tell me what can go wrong if I do not await the axios request.
```

## 1:50 PM - 2:25 PM: Authenticated Requests And Protected Routes

Teach the authenticated request header:

```js
headers: {
  Authorization: `Bearer ${localStorage.getItem("access_token")}`,
}
```

Create a reusable helper:

```js
export const authRequest = async (method, url, data = null) => {
  return axios({
    method,
    url: `${BASE_URL}${url}`,
    data,
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
  });
};
```

Then use:

```js
const response = await authRequest("get", "/profile/");
```

Protected route concept:

```jsx
return isAuthenticated ? children : <Navigate to="/login" />;
```

Teach:

- Protected frontend routes improve user experience.
- Backend permissions are still required.
- Hiding a page in React is not real security.
- Real security happens on the backend with `IsAuthenticated` and user filtering.

AI adoption moment:

Students ask AI:

```text
Review this protected route and authenticated request helper. What security is frontend-only, and what must still be enforced by Django?
```

Teaching point:

Authorization must be enforced by the backend, not only by React.

## 2:25 PM - 2:40 PM: Break

Quick check:

- Can students log in?
- Do tokens appear in localStorage?
- Can they call a protected endpoint?
- Do they understand why `Bearer` is needed?

## 2:40 PM - 3:15 PM: Add To Cart And Cart Display

Teach cart as the first user action that changes backend data.

Endpoint examples:

```text
POST /cart/add/
GET /cart/
PUT /cart/update/<id>/
DELETE /cart/delete/<id>/
```

Add to cart request body:

```json
{
  "product_id": 1,
  "qty": 1
}
```

Example:

```js
const handleAddToCart = async (productId) => {
  try {
    await authRequest("post", "/cart/add/", {
      product_id: productId,
      qty: 1,
    });

    alert("Added to cart");
  } catch (error) {
    console.error(error.response?.data || error.message);
  }
};
```

Cart display:

```js
const response = await authRequest("get", "/cart/");
setCartItems(response.data);
```

Teach:

- Product list/detail can be public.
- Add to cart must be authenticated.
- The frontend sends `product_id` and `qty`.
- The backend decides which user owns the cart item from the token.
- The frontend should not send `user_id` for the cart owner.

AI adoption moment:

Students ask AI:

```text
My add-to-cart request returns 401 or 400. Ask me for the request body, headers, and Django serializer before suggesting a fix.
```

Common debugging checklist:

- Is the user logged in?
- Is the access token in localStorage?
- Is the `Authorization` header present?
- Is the endpoint path correct?
- Does the body use `product_id`, not `product`?
- Is `qty` a valid number?

## 3:15 PM - 3:40 PM: View Orders

Teach orders as protected user-owned data.

Endpoint:

```text
GET /orders/
```

Expected concept:

- The backend returns only the logged-in user's orders.
- Orders may include total price, paid status, shipping info, and order items.
- The frontend renders the list.

Example:

```js
const fetchOrders = async () => {
  try {
    const response = await authRequest("get", "/orders/");
    setOrders(response.data);
  } catch (error) {
    console.error(error.response?.data || error.message);
  }
};
```

Simple UI approach:

- If there are no orders, show "No orders yet."
- For each order, show order ID, total, paid status, and item count.
- Do not overbuild the UI today.

Teach:

- Orders are private.
- Backend must filter by `request.user`.
- Frontend should never request all users' orders.
- API response shape matters. Students should inspect the JSON before building the UI.

AI adoption moment:

Students ask AI:

```text
Here is my /orders/ JSON response. Help me design a simple React component to display it, but keep the component beginner-friendly.
```

Teaching point:

Students should paste sample JSON into AI before asking for UI help. AI writes better frontend code when it knows the actual response shape.

## 3:40 PM - 4:00 PM: Integration Review And Reflection

End by making students explain the full flow.

Ask:

- What happens when the homepage loads products?
- What happens when a user registers?
- What happens when a user logs in?
- Where is the access token stored?
- How does the backend know which user owns the cart?
- Why should the frontend not send `user_id` for cart actions?
- What did AI help debug today?
- What AI answer did you need to correct or simplify?

Exit ticket:

Students submit:

- Screenshot of products loaded from Django.
- Screenshot of successful registration or login.
- Screenshot of token response or protected endpoint success.
- Screenshot of add-to-cart working.
- Screenshot of cart or orders page.
- One AI prompt they used for debugging.
- One fullstack bug they solved.

## Recommended Instructor Flow

Use this rhythm throughout Day 3:

1. Show the backend endpoint.
2. Show the expected request body.
3. Show the expected response.
4. Write the React request.
5. Log the response.
6. Render the data.
7. Add loading and error states.
8. Ask AI to review the integration.
9. Fix only the most important issue.

This makes fullstack integration less mysterious.

## Assessment Rubric

### Beginner Passing Output

The student has:

- React frontend calling Django `/products/`.
- Product data rendered from the backend.
- Register form connected to backend or attempted clearly.
- Login form connected to JWT endpoint.
- Tokens stored after login.
- At least one authenticated request attempted.
- Add-to-cart request attempted.

### Strong Output

The student also has:

- Working register and login.
- Protected route behavior.
- Reusable `BASE_URL`.
- Reusable authenticated request helper.
- Add to cart works with JWT token.
- Cart page displays backend cart items.
- Orders page displays backend orders.
- Loading and error states.
- Student can explain the request-response flow.

### Needs Improvement

The student may need help if:

- They hardcode products even though the API works.
- They cannot explain where the token comes from.
- They send cart requests without the `Authorization` header.
- They send `user_id` from the frontend for cart ownership.
- They copy AI-generated code with unknown hooks or libraries.
- They only know "it works" but cannot trace the API flow.

## AI Rules For Day 3

Allowed AI use:

- Explain API errors.
- Compare frontend request body with backend serializer fields.
- Review Axios calls.
- Explain JWT headers.
- Suggest loading and error states.
- Help simplify a component.
- Review whether an endpoint should be public or protected.

Not allowed without review:

- Replacing the whole frontend with AI-generated code.
- Changing backend endpoint names without updating the frontend.
- Adding new auth libraries not taught in class.
- Ignoring CORS or token errors by disabling security.
- Copying token refresh code without understanding it.

Required student habit:

Before asking AI to fix an integration bug, students should collect:

```text
1. Endpoint URL
2. HTTP method
3. Request body
4. Request headers
5. Status code
6. Response error
7. Backend serializer/view involved
```

This makes AI much more useful and teaches professional debugging.

## Suggested Homework

Students should finish or improve:

- Product list from backend.
- Product detail from backend.
- Register page.
- Login page.
- Protected profile page.
- Add-to-cart button.
- Cart page.
- Basic orders page.

AI homework rule:

Students may use AI, but must include an `AI_NOTES.md` or homework note with:

- Prompts used.
- Error messages AI helped explain.
- Code accepted from AI.
- Code changed manually.
- One AI suggestion rejected and why.

Optional challenge:

- Add automatic token refresh.
- Add logout that clears tokens.
- Add a profile page using `/profile/`.
- Display backend validation errors under form inputs.
- Create a small `apiClient.js` file for all Axios logic.

## Instructor Notes For Your Existing Project

Your current project already has many Day 3 pieces:

- `frontend/src/api/base.js` for `BASE_URL`
- `frontend/src/api/Auth_refresh.js` for authenticated API requests
- `frontend/src/context/AuthProvider.jsx` for auth state
- `frontend/src/context/PrivateRoute.jsx` for route protection
- `frontend/src/pages/Login.jsx` for JWT login
- `frontend/src/pages/Cart.jsx` for cart display and checkout
- `frontend/src/pages/Profile.jsx` for profile and future orders
- Backend routes for products, register, login, cart, profile, and orders

Use the project as a teaching reference, but also show its current issues as learning opportunities:

- Fix the product route mismatch between `/products/:id` and `/product/${id}`.
- Add the missing frontend register route/page.
- Make login navigation happen after the async request succeeds.
- Use the authenticated request helper consistently.
- Replace placeholder purchase history with real `/orders/` data.

The best closing line for students:

> Today your frontend stopped being a picture and started becoming an application. The browser is now talking to the database through your API.
