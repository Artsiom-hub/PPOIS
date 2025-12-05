# infrastructure/api/dependencies.py

from fastapi import Depends
from Core_Domains.book_catalog.services import BookCatalogService
from Core_Domains.book_catalog.repository_interface import BookRepository
from Core_Domains.Order_Processing.services import OrderService
from Core_Domains.Order_Processing.repository_interface import OrderRepository
from Core_Domains.Payments.services import PaymentService
from Core_Domains.Payments.repository_interface import AccountRepository, TransactionRepository
from Core_Domains.User_Security.services import UserService
from Core_Domains.User_Security.auth_service import AuthService
from Core_Domains.User_Security.repository_interface import UserRepository, RoleRepository
from Core_Domains.Warehouse.services import WarehouseService
from Infrastructure.integrations.email.smtp_service import SmtpEmailService
from Infrastructure.integrations.payments.bank_gateway import BankGateway
from Infrastructure.integrations.logging.audit_logger import AuditLogger
from Infrastructure.integrations.notifications.telegram_notifier import TelegramNotifier
from Core_Domains.Warehouse.repository_interface import (
    CellRepository, StockRepository, StockMovementRepository, InventorySessionRepository
)
from Infrastructure.Persistence_Layer.in_memory.book_repo import InMemoryBookRepository
from Infrastructure.Persistence_Layer.in_memory.order_repo import InMemoryOrderRepository
from Infrastructure.Persistence_Layer.in_memory.payments_repo import (
    InMemoryAccountRepository, InMemoryTransactionRepository
)
from Infrastructure.Persistence_Layer.in_memory.user_repo import (
    InMemoryUserRepository, InMemoryRoleRepository, InMemoryPermissionRepository
)
from Infrastructure.Persistence_Layer.in_memory.warehouse_repo import (
    InMemoryCellRepository, InMemoryStockRepository,
    InMemoryStockMovementRepository, InMemoryInventorySessionRepository
)
book_repo = InMemoryBookRepository()
order_repo = InMemoryOrderRepository()
account_repo = InMemoryAccountRepository()
trx_repo = InMemoryTransactionRepository()
user_repo = InMemoryUserRepository()
role_repo = InMemoryRoleRepository()
perm_repo = InMemoryPermissionRepository()
cell_repo = InMemoryCellRepository()
stock_repo = InMemoryStockRepository()
movement_repo = InMemoryStockMovementRepository()
inventory_repo = InMemoryInventorySessionRepository()

# ================================
# Здесь должны быть твои реальные
# или in-memory реализации репозиториев.
# Для примера — простые in-memory словари.
# ================================


# ================================
# Сервисы
# ================================
book_service = BookCatalogService(book_repo)
order_service = OrderService(order_repo, book_repo)
payment_service = PaymentService(account_repo, trx_repo, gateway=None)
user_service = UserService(user_repo, role_repo)
auth_service = AuthService(user_repo)
warehouse_service = WarehouseService(
    cell_repo, stock_repo, movement_repo, inventory_repo
)

# ================================
# FastAPI зависимость для DI
# ================================

def get_book_service():
    return book_service

def get_order_service():
    return order_service

def get_payment_service():
    return payment_service

def get_user_service():
    return user_service

def get_auth_service():
    return auth_service

def get_warehouse_service():
    return warehouse_service
