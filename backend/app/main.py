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


@app.get("/")
def home():
    return {"message": "Welcome to Domino's Food Ordering API"}