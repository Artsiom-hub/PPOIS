Currency 3 3 →
Money 2 6 → Currency
Address 4 3 →
Email 1 2 →
PhoneNumber 1 2 →
PersonName 2 2 →
ISBN 1 4 →
BookId 1 1 →
CustomerId 1 1 →
PasswordHash 1 3 →
OrderId 1 1 →
DeliveryMethod 3 2 → Money
WarehouseLocation 3 2 → Address
NotificationChannel 2 2 →
AuditLogEntry 4 2 →

Author 3 2 → PersonName
Publisher 3 2 → Address
Category 3 2 →
Tag 1 2 →
Book 7 4 → Author, Publisher, Category, Tag, Money
BookCopy 3 3 → Book
Review 5 2 → Book, CustomerAccount
BookSearchEngine 2 3 → Book
Reservation 4 3 → Book, CustomerAccount
DiscountCode 3 2 →

Shelf 4 3 → BookCopy
Aisle 3 3 → Shelf
StockItem 3 3 → Book, WarehouseLocation
Inventory 1 4 → StockItem
Warehouse 4 3 → Aisle, Inventory, WarehouseLocation
ShipmentTracking 3 3 →
Shipment 4 3 → Order, DeliveryMethod, ShipmentTracking
Supplier 3 2 → Email

LoyaltyTier 3 2 →
LoyaltyAccount 3 3 → LoyaltyTier
CustomerAccount 6 3 → PersonName, Email, Address, PasswordHash, LoyaltyAccount
CartItem 2 2 → Book
ShoppingCart 2 3 → CartItem
Notification 4 2 → CustomerAccount, NotificationChannel
AccessPolicy 2 2 →

OrderLine 3 2 → Book, Money
Order 5 4 → CustomerAccount, OrderLine
PaymentCard 5 3 → Money, PersonName
PaymentTransaction 5 3 → PaymentCard, Money
PaymentGateway 1 2 → PaymentTransaction
Invoice 3 2 → Order, Money
ReturnRequest 4 3 → Order

UserSession 4 3 → CustomerAccount, AccessPolicy
ReportGenerator 1 3 → Order

Exceptions 1 12 → BookNotFoundError, OutOfStockError, DuplicateISBNError, InvalidISBNError, CustomerNotFoundError, InvalidPasswordError, PaymentDeclinedError, InsufficientFundsError, UnauthorizedAccessError, WarehouseCapacityError, OrderStateError, LoyaltyPointsError

Исключения (12):
BookNotFoundError 0 0 →
OutOfStockError 0 0 →
DuplicateISBNError 0 0 →
InvalidISBNError 0 0 →
CustomerNotFoundError 0 0 →
InvalidPasswordError 0 0 →
PaymentDeclinedError 0 0 →
InsufficientFundsError 0 0 →
UnauthorizedAccessError 0 0 →
WarehouseCapacityError 0 0 →
OrderStateError 0 0 →
LoyaltyPointsError 0 0 →

Поля: 155
Поведения: 118
Ассоциации: 34
Исключения: 12
