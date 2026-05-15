# Day 4 Teaching Plan: PayMongo Checkout, Orders, Production Prep, and Deployment

## Class Context

**Class time:** 9:00 AM to 4:00 PM  
**Main goal:** Students integrate payment processing, connect successful payments to orders, prepare the app for production, and deploy the project.  
**AI goal:** Students learn how to use AI for payment-flow review, deployment checklists, environment-variable setup, debugging logs, and production-readiness checks without blindly trusting generated payment or security code.

Day 4 is the capstone day. Students move from a working fullstack app to a deployable e-commerce app with checkout.

The teaching theme should be:

```text
Working locally is not the same as ready for users.
```

Payment and deployment code must be taught more carefully than layout or simple CRUD. It touches money, credentials, user data, external APIs, webhooks, production domains, and real error cases.

Important instructor note:

Use PayMongo test mode for class. Students should not use live payment keys or live payment methods during training.

## Learning Outcomes

By the end of Day 4, students should be able to:

- Explain the checkout flow from cart to payment provider to order record.
- Create a backend checkout endpoint that computes totals from the database.
- Send a payment request to PayMongo from the Django backend.
- Redirect the user from React to a hosted checkout/payment page.
- Understand why payment confirmation should happen through webhooks, not only frontend redirects.
- Connect successful payment events to order creation.
- Store payment/order records in the database.
- Move secrets into environment variables.
- Prepare Django and React for production deployment.
- Deploy the backend and frontend.
- Use AI to review payment and deployment risks.
- Read deployment logs and debug common production issues.

## Recommended Schedule

### 9:00 AM - 9:30 AM: Recap And Payment Flow Mental Model

Start by reviewing the full app journey:

```text
Homepage -> Product detail -> Add to cart -> Cart page -> Checkout -> Payment -> Order history
```

Then draw the payment flow:

```text
React cart page
  -> POST /checkout/
  -> Django computes total from cart
  -> Django creates payment session/link with PayMongo
  -> Django saves pending payment record
  -> React redirects user to PayMongo checkout
  -> User pays
  -> PayMongo sends webhook to Django
  -> Django marks payment as paid
  -> Django creates order items
  -> User sees order history
```

Core teaching point:

The frontend should not decide that an order is paid. The backend should confirm payment using PayMongo's trusted server-to-server notification.

AI adoption moment:

Students ask AI:

```text
Explain a payment checkout flow for a Django and React e-commerce app. Include frontend redirect, backend payment record, webhook confirmation, and order creation.
```

Class discussion:

- Which steps happen in React?
- Which steps happen in Django?
- Which steps happen in PayMongo?
- Which step actually proves payment succeeded?

## 9:30 AM - 10:15 AM: Payment Data Model And Order Flow

Before calling PayMongo, teach students what must be stored locally.

Minimum records:

- Payment or order header
- Order items
- Shipping address, if needed
- Payment provider reference ID
- Payment status
- Paid timestamp

Recommended simple model concepts:

```text
Payment
  user
  totalPrice
  isPaid
  paidAt
  providerPaymentId
  providerStatus

OrderItem
  payment/order
  product
  qty
  price

ShippingAddress
  payment/order
  fullName
  address
  city
  postalCode
  country
```

Teach:

- Store the product price at checkout time.
- Do not only rely on the current product price later.
- Orders should remain accurate even if a product price changes next week.
- Payment status starts as pending/unpaid.
- Payment status becomes paid only after confirmation.

Important validation:

- Cart must not be empty.
- Quantity must be valid.
- Product must still exist.
- Product must have enough stock, if stock tracking is included.
- Total must be computed on the backend.

AI adoption moment:

Students ask AI:

```text
Review this e-commerce order model. What data should be saved before redirecting the customer to payment, and what data should be saved after payment succeeds?
```

Teaching point:

AI is useful for modeling questions, but students must understand the business reason behind each field.

## 10:15 AM - 10:30 AM: Break

Quick check:

- Can students explain why order items need their own price field?
- Can students explain why frontend totals are not trusted?
- Can students explain what "pending payment" means?

## 10:30 AM - 11:30 AM: Create Checkout Endpoint

Build or explain a backend endpoint:

```text
POST /checkout/gcash/
```

Request body example:

```json
{
  "fullName": "Juan Dela Cruz",
  "address": "123 Sample Street",
  "city": "Manila",
  "postalCode": "1000",
  "country": "Philippines"
}
```

Backend responsibilities:

1. Require authentication.
2. Validate shipping data.
3. Load cart items for `request.user`.
4. Reject empty cart.
5. Compute total from product prices in the database.
6. Create the PayMongo checkout/payment request.
7. Save a pending payment record.
8. Save shipping address.
9. Return the checkout URL to React.

Important rule:

The frontend should not send `totalPrice`. If it does, the backend should ignore it and compute the total again.

Example response:

```json
{
  "checkout_url": "https://..."
}
```

React receives this response and redirects:

```js
window.location.href = response.data.checkout_url;
```

AI adoption moment:

Students ask AI:

```text
Review this Django checkout endpoint for trust issues. Does it trust the frontend too much? Does it compute totals safely? Does it save payment state before redirecting?
```

Instructor warning:

Do not let students put PayMongo secret keys in React. Payment provider secret keys belong only on the backend.

## 11:30 AM - 12:00 PM: PayMongo Integration Concepts

Teach PayMongo integration as a backend-to-provider request.

Important concepts:

- Use test keys during class.
- Store secret keys in environment variables.
- Backend creates the checkout/payment request.
- PayMongo returns a hosted checkout URL or payment link/session.
- The browser redirects the customer to PayMongo.
- PayMongo later notifies the backend using a webhook.

Simple classroom explanation:

```text
React asks Django to start checkout.
Django asks PayMongo to create a payment page.
PayMongo gives Django a checkout URL.
Django gives that URL to React.
React sends the user to PayMongo.
```

Security rules:

- Never expose secret keys in frontend code.
- Never commit API keys to Git.
- Never trust a success redirect alone.
- Always verify webhook authenticity.
- Keep test and live keys separate.

AI adoption moment:

Students ask AI:

```text
Explain why a payment provider secret key must stay on the backend and should never be placed in React code.
```

Optional instructor note:

PayMongo supports hosted checkout-style integrations and webhook notifications. Since payment provider APIs can change, always check the current official PayMongo documentation before teaching exact payload fields.

## 12:00 PM - 1:00 PM: Lunch

Optional lunch task:

Students write a plain-English checkout flow in 8 to 10 steps. This is more valuable than writing code they do not understand.

## 1:00 PM - 1:45 PM: Webhook To Order Creation

Teach webhooks slowly. This is often the hardest part for students.

Simple explanation:

```text
A webhook is a request sent by PayMongo to your backend when something important happens.
```

Why webhooks matter:

- The user may close the browser after payment.
- Redirect URLs can be faked or interrupted.
- The backend needs a trusted server-to-server confirmation.
- Payment providers may retry webhook events.

Webhook endpoint example:

```text
POST /webhook/paymongo/
```

Webhook responsibilities:

1. Receive event from PayMongo.
2. Verify the webhook signature.
3. Check event type.
4. Find the matching local payment record.
5. If already paid, return success without creating duplicate orders.
6. Mark payment as paid.
7. Create order items from cart items.
8. Clear the cart.
9. Return a success response.

Important classroom warning:

Using `csrf_exempt` for a webhook is normal, but it does not mean the endpoint should trust every request. It still needs signature verification.

Idempotency concept:

```text
If PayMongo sends the same paid event twice, the app should not create duplicate order items.
```

AI adoption moment:

Students ask AI:

```text
Review this webhook handler. Is it idempotent? Does it verify the provider signature? Could duplicate events create duplicate orders?
```

Teaching point:

Webhook code that "works once" is not enough. It must work safely when called twice, called late, or called with invalid data.

## 1:45 PM - 2:20 PM: Frontend Checkout And Orders UX

Teach the user-facing side.

Cart page responsibilities:

- Show cart items.
- Collect shipping details.
- Show subtotal and total.
- Disable checkout if cart is empty.
- Send shipping data to backend checkout endpoint.
- Redirect to PayMongo checkout URL.

After payment:

- A success redirect page can thank the user.
- The real order status should come from the backend.
- The profile/orders page should call `/orders/`.

Orders page responsibilities:

- Require login.
- Fetch orders from backend.
- Show paid/pending status.
- Show order items.
- Show total price.

AI adoption moment:

Students ask AI:

```text
Here is my order JSON response. Help me build a simple React orders section that shows order status, total, and item names. Keep it beginner-friendly.
```

Teaching point:

Students should inspect JSON first before designing the UI.

## 2:20 PM - 2:35 PM: Break

Quick check:

- Does checkout return a URL?
- Does React redirect correctly?
- Can students explain webhook vs redirect?
- Can students explain why order history reads from the backend?

## 2:35 PM - 3:15 PM: Production Preparation

Teach production readiness as a checklist.

Backend production checklist:

- Move `SECRET_KEY` to environment variables.
- Move database credentials to environment variables.
- Move PayMongo keys to environment variables.
- Set `DEBUG=False`.
- Set `ALLOWED_HOSTS` to real domains.
- Configure CORS for the deployed frontend domain only.
- Configure database for production PostgreSQL.
- Run migrations.
- Configure static and media files.
- Add `requirements.txt`.
- Add `runtime.txt` if the host needs it.
- Confirm `gunicorn` works.
- Add logging for payment and webhook errors.

Frontend production checklist:

- Move backend URL into environment variable.
- Build with production backend URL.
- Remove unnecessary `console.log`.
- Confirm all routes work after refresh.
- Confirm protected routes still redirect correctly.
- Confirm login/register/cart/orders use deployed backend URL.
- Confirm images load correctly.

Repository checklist:

- Add `.gitignore`.
- Do not commit `venv/`.
- Do not commit `.env`.
- Do not commit `__pycache__/`.
- Do not commit local database files unless intentionally included for class.
- Keep `.env.example` with fake values.
- Write setup instructions in README.

AI adoption moment:

Students ask AI:

```text
Act as a deployment reviewer. Review this Django + React e-commerce project checklist before production. Focus on secrets, DEBUG, allowed hosts, CORS, database, static files, and payment webhooks.
```

Teaching point:

AI is excellent for checklists, but it cannot verify your production environment unless you provide logs, settings, and exact errors.

## 3:15 PM - 3:45 PM: Deployment

Teach deployment as two separate deployments:

```text
Backend deploy
Frontend deploy
```

Backend deploy flow:

1. Push code to GitHub or chosen repository.
2. Create backend service on hosting platform.
3. Set build/start commands.
4. Add environment variables.
5. Connect PostgreSQL database.
6. Run migrations.
7. Confirm backend health route or admin route.
8. Test `/products/`.
9. Test `/api/token/`.
10. Test protected endpoint.

Frontend deploy flow:

1. Set frontend environment variable for backend URL.
2. Build frontend.
3. Deploy to frontend host.
4. Confirm homepage loads.
5. Confirm products load from backend.
6. Confirm login works.
7. Confirm cart requests reach deployed backend.

Payment deployment flow:

1. Configure PayMongo webhook URL to deployed backend endpoint.
2. Use HTTPS webhook URL.
3. Select correct webhook events.
4. Store webhook secret in backend environment variables.
5. Test payment in test mode.
6. Confirm webhook logs.
7. Confirm order appears after payment.

Suggested platforms:

- Backend: Render, Railway, Fly.io, or similar.
- Frontend: Vercel, Netlify, or similar.
- Database: managed PostgreSQL from the backend host or external provider.

Do not over-focus on the platform. The important concepts are environment variables, build commands, deployed URLs, CORS, and logs.

AI adoption moment:

Students ask AI:

```text
I deployed my Django backend and got this log error: [paste logs]. Explain the likely cause and ask me for missing settings before giving a fix.
```

Common deployment problems:

- Missing environment variable.
- Wrong backend URL in frontend.
- CORS not allowing deployed frontend.
- `ALLOWED_HOSTS` missing deployed backend domain.
- Database migrations not run.
- Static/media files not configured.
- Payment webhook URL still points to localhost.
- Secret key changed unexpectedly.

## 3:45 PM - 4:00 PM: Final Review And Capstone Reflection

End with a final system walkthrough.

Students should explain:

- How checkout starts.
- Why backend computes the total.
- Where the PayMongo secret key lives.
- Why a webhook is needed.
- How a payment becomes an order.
- What must change before deployment.
- How frontend and backend deployed URLs connect.
- What AI helped with.
- What AI should not be trusted to do automatically.

Exit ticket:

Students submit:

- Screenshot of checkout page or checkout URL response.
- Screenshot of deployed frontend.
- Screenshot of deployed backend endpoint.
- Screenshot of environment variables list with values hidden.
- Screenshot or note showing webhook configuration.
- One deployment error they fixed.
- One AI prompt they used.
- One production-readiness rule they will remember.

## Recommended Instructor Flow

Use this rhythm:

1. Draw the payment flow before coding.
2. Show the backend checkout endpoint.
3. Show the React checkout request.
4. Show PayMongo redirect.
5. Explain webhook confirmation.
6. Show order history.
7. Review secrets and production settings.
8. Deploy backend.
9. Deploy frontend.
10. Test the full flow.

This keeps students from thinking payment is just a button click.

## Assessment Rubric

### Beginner Passing Output

The student has:

- Checkout endpoint attempted or working.
- Backend computes total from cart.
- Payment provider secret key is not in React.
- React checkout button calls backend.
- App redirects to payment page or receives checkout URL.
- Basic production checklist completed.
- Frontend or backend deployed.

### Strong Output

The student also has:

- Pending payment record saved before redirect.
- Webhook endpoint implemented.
- Webhook handler verifies authenticity or clearly marks verification as required before production.
- Payment success creates order items.
- Cart clears after successful payment.
- Orders page displays real backend orders.
- Backend and frontend both deployed.
- Environment variables are used for secrets and URLs.
- Student can explain the full checkout-to-order flow.

### Needs Improvement

The student may need help if:

- They put PayMongo secret keys in React.
- They trust the frontend success redirect as proof of payment.
- They accept frontend total price without backend recomputation.
- They cannot explain webhook purpose.
- They deploy with `DEBUG=True`.
- They use `ALLOWED_HOSTS=["*"]` without understanding the risk.
- They commit `.env`, `venv/`, or real credentials.
- They copy AI payment code without reviewing security.

## AI Rules For Day 4

Day 4 AI rules must be strict because payment and deployment mistakes can be serious.

Allowed AI use:

- Explain payment flow.
- Review checkout endpoint risks.
- Review webhook idempotency.
- Explain deployment logs.
- Generate deployment checklist.
- Explain environment variables.
- Suggest README deployment instructions.
- Help debug CORS or `ALLOWED_HOSTS` errors.

Not allowed without instructor review:

- AI-generated payment code used directly in production.
- AI-generated webhook verification used without checking provider docs.
- AI-generated deployment settings with fake or exposed secrets.
- AI suggestions to disable security to "make it work."
- Moving secret keys into frontend code.
- Skipping webhook verification because redirects appear to work.

Required student habit:

Before accepting AI suggestions for payment or deployment, students must answer:

```text
Does this expose a secret?
Does this trust the frontend too much?
Does this verify the payment provider?
Does this work if the webhook is sent twice?
Does this still work after deployment?
Can I explain the failure mode?
```

## Suggested Homework

Students should finish or improve:

- Environment variable setup.
- `.env.example`
- `.gitignore`
- Checkout endpoint.
- Webhook endpoint.
- Orders page.
- Deployment README.
- Screenshots of deployed app.

AI homework rule:

Students may use AI, but must include:

- Prompts used.
- Deployment errors pasted into AI.
- Suggestions accepted.
- Suggestions rejected.
- Security concern discovered by AI or by the student.

Optional challenge:

- Add payment failed page.
- Add payment pending page.
- Add order status refresh.
- Add stock reduction after successful payment.
- Add webhook event logging.
- Add a health-check endpoint for deployment.
- Add automated tests for checkout and webhook idempotency.

## Instructor Notes For Your Existing Project

Your current project already has many Day 4 pieces:

- Checkout endpoint in `backend/base/views.py`
- PayMongo request logic in `create_gcash_payment`
- Payment/order models in `backend/base/models.py`
- Webhook handler in `paymongo_webhook`
- `mark_paid()` method that creates order items and clears the cart
- Orders endpoint in `list_user_orders`
- Frontend checkout logic in `frontend/src/pages/Cart.jsx`

Use these as live teaching material, but also be honest about improvements needed:

- Move PayMongo and database secrets to environment variables.
- Verify webhook signatures.
- Do not rely only on redirect success.
- Replace localhost redirect URLs with environment-based deployed URLs.
- Configure production CORS and allowed hosts.
- Add tests for empty cart, duplicate webhook events, and order creation.
- Remove `DEBUG=True` for production.
- Add `.gitignore` and remove generated/local files from tracking.

Recommended Day 4 boundary:

- Teach test-mode checkout.
- Teach webhook concept and safe handler design.
- Teach production checklist.
- Deploy a working version.
- Do not rush live payments.

The best closing line for students:

> A deployed app is not finished because it is online. It is finished when it is online, secure, understandable, and recoverable when something breaks.
