from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import admin, auth, countries, orders, products
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers

app = FastAPI(
    title="Game Items Store API",
    version="1.0.0",
    description="Login, browse digital game items (JO/SA), view details, and buy one item per order.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(countries.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
