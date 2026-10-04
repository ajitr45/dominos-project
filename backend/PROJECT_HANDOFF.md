# DOMINO'S-STYLE FASTAPI PROJECT — MASTER HANDOFF CONTEXT

## 1. PROJECT GOAL

I am building a Domino's-style food ordering backend as a real production-oriented learning project.

Tech stack:
- Python 3.10
- FastAPI
- SQLAlchemy 2.0.52
- SQLite for now
- Alembic 1.20.0
- Uvicorn
- Pydantic
- JWT authentication
- pwdlib/password hashing

Important:
Use SQLite for now. PostgreSQL migration can happen later.

This is NOT a generic tutorial project.
All future code, models, schemas, APIs, database fields, services, routers and architecture must be designed according to THIS project's actual requirements.

---

# 2. VERY IMPORTANT WORKING RULES

Follow these rules strictly:

1. Do not unnecessarily change existing code.

2. Do not refactor working code just for style.

3. If an existing model, schema, route, migration, database state or workflow needs to change:
   - explain WHY
   - explain EXACTLY what will change
   - ask for permission
   - only then provide/apply the change.

4. Do not directly return query/function results.
   Store the result in a meaningful variable first, then return it.

Example:

BAD:
return get_dashboard_data(db)

GOOD:
dashboard_data = get_dashboard_data(db)
return dashboard_data

5. Keep the project production-oriented from the beginning so that repeated future refactoring is minimized.

6. Explain important code while teaching:
   - what it does
   - why it is used
   - how it works
   - why this approach is appropriate for this project
   - mention alternatives only when relevant.

7. Do not create unnecessary helper functions.

8. Do not jump ahead.
When I say "next", continue with only the next logical step.

9. For testing:
   - one test at a time
   - tell me exactly what request/command to run
   - wait for my result
   - then continue.

10. Comments inside code should be in English.

11. Review code carefully before moving to the next step.

12. Migration:
   - review migration first
   - do not blindly apply changes
   - do not create migrations unless actually required.

13. Production-ready does not mean blindly adding complexity.
Keep the implementation simple, secure and maintainable.

---

# 3. PROJECT ROADMAP

1. Project Setup
2. Database Setup
3. User CRUD
4. Categories
5. Products
6. Database Relationships
7. Authentication
8. Cart
9. Addresses
10. Orders
11. Payment
12. Admin
13. Testing + Security
14. Deployment

---

# 4. PROJECT STRUCTURE

dominos_project/
├── backend/
└── frontend/

backend/
├── env/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── category_service.py
│   │   ├── product_service.py
│   │   ├── product_variant_service.py
│   │   ├── size_service.py
│   │   ├── cart_service.py
│   │   ├── address_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   └── admin_service.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── categories.py
│   │   ├── products.py
│   │   ├── product_variants.py
│   │   ├── sizes.py
│   │   ├── cart.py
│   │   ├── addresses.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   └── admin.py
│   └── dependencies/
│       ├── __init__.py
│       └── auth.py
├── alembic/
├── alembic.ini
├── dominos.db
├── .env
├── .gitignore
└── requirements.txt

---

# 5. DATABASE TABLES

Current/planned tables:

users
categories
products
product_variants
sizes
carts
cart_items
addresses
orders
order_items
payments

Future production customization tables may be added later if actually required:

customization_groups
customization_options
order_item_customizations

---

# 6. RELATIONSHIPS

users
 ├── addresses
 ├── carts
 │    └── cart_items
 └── orders
      └── order_items

categories
 └── products
      └── product_variants
           └── sizes

orders
 └── payments

---

# 7. DATABASE / ALEMBIC

Database:

SQLite

DATABASE_URL:

sqlite:///./dominos.db

SQLAlchemy:
2.0.52

Alembic:
1.20.0

Alembic is configured with:
target_metadata = Base.metadata

Current migration chain:

35095c702526
↓
2c494e3c4ccf
↓
421c78ba9fd3
↓
e22f629c1ac6
↓
10dbba6bde9f
↓
daf3d2b2edcc
↓
70a136f4b6ad
↓
597714def8a2
↓
3de9b55509db
↓
4f1f33df3ef2
↓
c631e8dd1068
↓
88adce94a1b2
↓
527052c144a3
↓
985bd37677e7
↓
39f5add42524
↓
66a522f43073
↓
82f564172cfe
↓
0c651903eea4
↓
adfce388e4d9
↓
e54f64394309

Latest migration:
e54f64394309
Purpose:
payment amount non-negative constraint

Constraint:
ck_payments_amount_non_negative

Migration was manually corrected because autogenerate produced an empty migration.

It has already been applied successfully with:

alembic upgrade head

Do NOT create duplicate migrations for already-existing changes.

---

# 8. USER MODEL

Important fields:

id
username
email
password_hash
phone
role
is_active
created_at
updated_at

User roles:

CUSTOMER = "customer"
ADMIN = "admin"
DELIVERY_BOY = "delivery_boy"
MANAGER = "manager"

---

# 9. AUTHENTICATION

JWT authentication is already implemented.

Config includes:

JWT_SECRET_KEY
JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES
JWT_REFRESH_TOKEN_EXPIRE_DAYS

Security includes:
- password hashing
- password verification
- access tokens
- refresh tokens
- refresh token rotation
- refresh token revocation
- password change
- password reset
- role-based authorization

Role dependencies exist:

require_admin
require_delivery_boy
require_manager
require_admin_or_manager
require_customer

Important:
Do not create unnecessary additional auth helper functions.

Auth tests already passed:

- login → 200
- refresh rotation → 200
- old refresh token reuse → 401
- password change → successful
- old refresh token after password change → 401
- new password login → 200
- password reset → successful
- reset token reuse → rejected
- logout → successful
- logged-out refresh token → rejected

---

# 10. CATEGORY MODULE

Category CRUD/management is implemented.

Features:
- create
- update
- deactivate
- activate
- public list
- public detail
- active-only behavior
- duplicate name protection
- case-insensitive duplicate handling
- admin/manager authorization

Roles:
Admin → allowed
Manager → allowed
Customer → forbidden

Important:
Category #7 "Test Category" was created during authorization testing.

It was:
created successfully
then deactivated
then activation endpoint was added/fixed
latest test:
PATCH /categories/7/activate → 200 OK

So Category #7 is currently active again.

Do not delete it unless explicitly instructed.

---

# 11. PRODUCT MODULE

Implemented:
- create
- update
- deactivate
- list
- detail
- active category validation
- active product filtering
- available variant filtering
- case-insensitive active duplicate product name protection

Existing product data includes:
- Farmhouse Pizza
- Peppy Paneer
- Garlic Bread etc.

Do not modify existing data without permission.

---

# 12. PRODUCT VARIANTS / SIZES

Sizes:
- Small
- Medium
- Large

Sizes are NOT hardcoded in APIs.

Product variants contain:
- product_id
- size_id
- price
- is_available
- is_active

Unique constraint:
product_id + size_id

Existing test variants include:
Farmhouse:
Small ₹199
Medium ₹299
Large ₹399

Peppy Paneer:
Small ₹249
Medium ₹369
Large ₹459

---

# 13. CART

Cart model has:
- active cart per user
- cart items
- quantity validation
- unique product variant per cart
- max quantity 20
- timestamps

Important constraints:
quantity >= 1
quantity <= 20

Cart behavior:
- get/create active cart
- add item
- duplicate variant merges quantity
- update item
- remove item
- product/variant/category availability validated
- cart totals calculated from current variant price

Cart tests passed:
- quantity update
- quantity 21 rejected
- remove item
- empty cart
- unavailable variant protection

Cart module is considered complete.
Do not unnecessarily modify it.

---

# 14. ADDRESS MODULE

Address fields:
user_id
label
recipient_name
phone
address_line1
address_line2
landmark
city
state
postal_code
is_default
is_active
timestamps

Features:
- create
- list
- detail
- update
- deactivate
- activate
- ownership validation
- one active default address per user
- soft deactivation

Validation:
- phone format
- postal code
- explicit null rejection in AddressUpdate
- omitted fields allowed for PATCH

Important:
Do not allow multiple active default addresses.

Address module is considered complete.

---

# 15. ORDER MODULE

Order statuses:

PENDING
CONFIRMED
PREPARING
OUT_FOR_DELIVERY
DELIVERED
CANCELLED

Order includes:
- user
- address
- delivery_boy
- status
- subtotal
- delivery_fee
- discount
- tax
- total_amount
- address snapshot
- order items

Order item stores product snapshot:
product_name
size_name
unit_price
quantity
subtotal

Important:
Order creation:
- requires active cart
- requires active owned address
- validates product/variant/category availability
- uses current price
- snapshots address/product/price data
- clears cart after successful order
- transaction-safe

Order status flow:

PENDING
→ CONFIRMED
→ PREPARING
→ OUT_FOR_DELIVERY
→ DELIVERED

Cancellation:
PENDING → CANCELLED
CONFIRMED → CANCELLED

Terminal:
DELIVERED
CANCELLED

Delivery boy flow:
PREPARING → OUT_FOR_DELIVERY → DELIVERED

Order tests passed:
- order creation
- cart clearing
- unavailable variant rejection
- address snapshot
- customer ownership
- delivery boy assignment
- invalid status transitions
- delivery boy status restrictions
- cancellation protection

Do not modify order workflow unnecessarily.

---

# 16. PAYMENT MODULE

Payment statuses:

PENDING
PAID
FAILED
REFUNDED

Payment methods:

COD
ONLINE

Payment fields:
- order_id
- user_id
- amount
- method
- status
- transaction_id
- razorpay_order_id
- razorpay_payment_id
- razorpay_signature
- timestamps

Important DB constraint:
amount >= 0

Payment order relationship:
one payment per order.

Payment security:
- amount comes from order.total_amount, NOT client
- ownership checked
- duplicate payment prevented
- customer cannot manually change payment status
- COD paid requires delivery-boy authorization
- COD can be marked paid only when order is OUT_FOR_DELIVERY
- already paid COD cannot be paid again
- cancelled orders cannot create payments

Payment state transitions:

PENDING → PAID
PENDING → FAILED
PAID → REFUNDED

FAILED and REFUNDED are terminal in current implementation.

Payment tests passed:
- COD create
- duplicate COD
- COD paid before delivery rejected
- COD paid successfully
- already-paid COD rejected
- payment ownership protection
- customer status update blocked
- invalid payment transition protection
- cancelled order payment blocked

Razorpay:
Razorpay code exists, but USER explicitly said:
"razorpay avoid kro abhi"

Therefore:
DO NOT continue Razorpay testing/integration right now.
It will be handled later.

Webhook code exists and has:
- signature verification
- JSON validation
- payment/order ID validation
- payment lookup
- amount validation
- INR currency validation
- duplicate paid protection
- payment captured handling
- payment failed handling
- transaction rollback
- order only moves PENDING → CONFIRMED from webhook

Webhook event-ID persistence is a future production improvement, but not currently required.

Actual Razorpay refund is also future work.

Payment module is currently frozen for the current COD scope.

---

# 17. ADMIN DASHBOARD

Admin dashboard is implemented.

No Dashboard database model was created because dashboard is an aggregation of existing tables.

Schema:

DashboardResponse:
- total_users
- active_users
- total_products
- active_products
- total_categories
- active_categories
- pending_orders
- confirmed_orders
- preparing_orders
- out_for_delivery_orders
- delivered_orders
- cancelled_orders
- pending_payments
- paid_payments

Service:
app/services/admin_service.py

Uses database-side aggregation:
- func.count
- conditional count
- group_by

Dashboard service uses approximately 5 DB queries:
- users
- products
- categories
- orders grouped by status
- payments grouped by status

Direct DB test passed.

Current dashboard data from DB:

total_users = 17
active_users = 16

total_products = 4
active_products = 2

total_categories = 6
active_categories = 3

pending_orders = 6
confirmed_orders = 0
preparing_orders = 0
out_for_delivery_orders = 2
delivered_orders = 6
cancelled_orders = 1

pending_payments = 2
paid_payments = 7

Router:
GET /admin/dashboard

Access:
Admin → 200
Manager → 200
Customer → 403
Delivery Boy → 403

Dashboard module is currently complete.

---

# 18. CURRENT ADMIN MANAGEMENT AUDIT

Category permission testing:

Customer → create category → 403
Manager → create category → 201
Manager → deactivate category → 200
Manager → activate category #7 → 200

Category #7 is active again.

Next audit should continue with:
- Product permissions
- Product Variant permissions
- Order management permissions
- Payment management permissions

Do not duplicate existing CRUD.

---

# 19. CURRENT FILE STATUS / ARCHITECTURE

Important files currently involved:

app/models.py
app/schemas.py
app/database.py
app/main.py

app/core/config.py
app/core/security.py

app/dependencies/auth.py

app/services/auth_service.py
app/services/category_service.py
app/services/product_service.py
app/services/product_variant_service.py
app/services/size_service.py
app/services/cart_service.py
app/services/address_service.py
app/services/order_service.py
app/services/payment_service.py
app/services/admin_service.py

app/routers/auth.py
app/routers/users.py
app/routers/categories.py
app/routers/products.py
app/routers/product_variants.py
app/routers/sizes.py
app/routers/cart.py
app/routers/addresses.py
app/routers/orders.py
app/routers/payments.py
app/routers/admin.py

---

# 20. MAIN.PY CURRENT ROUTER REGISTRATION

Current structure:

from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.categories import router as category_router
from app.routers.products import router as product_router
from app.routers.product_variants import router as product_variant_router
from app.routers.sizes import router as size_router
from app.routers.cart import router as cart_router
from app.routers.addresses import router as address_router
from app.routers.orders import router as orders_router
from app.routers.payments import router as payment_router
from app.routers import admin

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(product_variant_router)
app.include_router(size_router)
app.include_router(cart_router)
app.include_router(address_router)
app.include_router(orders_router)
app.include_router(payment_router)
app.include_router(admin.router)

@app.get("/")
def home():
    return {"message": "Welcome to Domino's Food Ordering API"}

---

# 21. CURRENT TESTING APPROACH

Always test one thing at a time.

For syntax:
python -m compileall <file>

For server:
uvicorn app.main:app --reload

Use Swagger/OpenAPI for API testing.

Do not make multiple unrelated changes before testing.

---

# 22. IMPORTANT PRODUCTION PRINCIPLES

Keep:
- database constraints
- ownership checks
- role authorization
- transaction rollback
- validation
- soft deletion where appropriate
- state machines
- indexes
- unique constraints
- snapshots for historical order data
- migration-based schema changes

Avoid:
- unnecessary abstraction
- unnecessary helper functions
- duplicate business logic
- direct query returns
- client-controlled payment amounts
- changing existing working code without permission
- hardcoded product sizes
- blindly creating migrations

---

# 23. WHERE WE ARE RIGHT NOW

Current active work:

ADMIN MODULE

Completed:
- Admin dashboard schema
- Admin dashboard service
- Admin dashboard router
- Router registration
- Admin access test
- Manager access test
- Customer rejection test
- Delivery Boy rejection test
- Category permission audit
- Category activate endpoint fixed

Latest successful log:

GET /admin/dashboard → 200 OK

Latest category test:

PATCH /categories/7/activate → 200 OK

Next logical step:
Continue Admin management permission audit with Products.

---

# 24. HOW TO CONTINUE IN NEW CHAT

First read this entire handoff.

Then DO NOT restart the project from the beginning.

Do NOT recreate existing models/services/routes.

First confirm:
1. You understand the project.
2. You understand current completed modules.
3. You understand the rules.
4. You understand the current exact next step.

Then say:
"Project context loaded. Current next step is Product permission audit."

Continue from there.
