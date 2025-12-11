# infrastructure/api/main.py

from fastapi import FastAPI
from .book_controller import router as book_router
from .order_controller import router as order_router
from .payments_controller import router as payments_router
from .user_controller import router as user_router
from .warehouse_controller import router as warehouse_router
from fastapi import FastAPI
from Infrastructure.Config.settings import get_settings
from Infrastructure.Config.logging_config import setup_logging

settings = get_settings()
setup_logging(settings.LOG_LEVEL)

app = FastAPI(title=settings.PROJECT_NAME)

app = FastAPI(title="Book Warehouse API")

app.include_router(book_router)
app.include_router(order_router)
app.include_router(payments_router)
app.include_router(user_router)
app.include_router(warehouse_router)
