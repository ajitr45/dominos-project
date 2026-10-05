from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})



app.add_middleware(CORSMiddleware, allow_origins=[ "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.get("/health")
def health_check():
    return {"status": "ok"}