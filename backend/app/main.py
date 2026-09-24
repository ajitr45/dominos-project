from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.categories import router as category_router
from app.routers.products import router as product_router
from app.routers.product_variants import router as product_variant_router


app = FastAPI()


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(product_variant_router)


@app.get("/")
def home():
    return {"message": "Welcome to Domino's Food Ordering API"}