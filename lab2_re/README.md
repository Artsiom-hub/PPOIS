Book 6 7 → Author, Price, Category
BookCatalog 4 8 → Book
User 7 5 → PasswordHash, Role
UserService 5 9 → UserRepository, AuthService
PasswordHash 2 4 →
Order 9 12 → User, OrderItem, Payment
OrderItem 5 4 → Book
OrderService 5 11 → OrderRepository, PaymentService, WarehouseService
Payment 5 6 → Money, Currency, Order
PaymentService 4 8 → PaymentGateway, PaymentRepository
Cell 5 4 →
StockItem 5 5 → Book, Cell
StockMovement 6 4 → StockItem
InventoryCheckSession 6 6 → InventoryCheckItem
InventoryCheckItem 5 3 → StockItem
WarehouseService 5 12 → StockRepository, CellRepository, InventorySessionRepository
BookRepository 0 5 →
UserRepository 0 6 →
OrderRepository 0 6 →
PaymentRepository 0 6 →
CellRepository 0 5 →
StockRepository 0 6 →
InventorySessionRepository 0 6 →
Money 2 4 →
Currency 3 2 →
Quantity 1 3 →
MovementType 1 0 →
Price 2 3 →

Exceptions (16):
BookNotFoundError 1 1 →
InvalidISBNError 0 0 →
DuplicateISBNError 0 0 →
InvalidPasswordError 0 0 →
UnauthorizedAccessError 0 0 →
InvalidCredentials 0 0 →
CustomerNotFoundError 0 0 →
PaymentDeclinedError 0 0 →
InsufficientFundsError 0 0 →
OrderStateError 0 0 →
LoyaltyPointsError 0 0 →
WarehouseCapacityError 0 0 →
DuplicateInventorySessionError 0 0 →
StockNotFoundError 0 0 →
InventorySessionNotFoundError 0 0 →
InvalidQuantityError 0 0 →

Поля: 172

Поведения : 188

Ассоциации: 63

Исключения: 16