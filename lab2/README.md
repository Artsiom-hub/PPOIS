BookCatalog 5 4 →
User 6 5 → AuthService, PasswordHasher
UserProfile 4 6 →
Book 6 3 →
Customer 3 6 →
PaymentProcessing 3 12 → PaymentGateway, TransactionManager, InvoiceGenerator
OrderManagement 6 7 → OrderService, Customer, Book
OrderProcessor 4 5 → Order, Customer, Book
Customer 6 7 → UserProfile, Book
UserCredentials 4 3 →
AuthService 8 4 →
Exceptions 1 11 → BookCatalogException, CustomerException, OrderException, etc.
ExpressOrder 12 11 → Order, Customer, Book
FragileBook 8 8 → Book
Location 4 4 →
SecurityManager 4 6 → AuthService
Insurance 7 4 → Book
Receipt 7 4 → Customer, Order
WarehouseManager 5 6 → AuthService, Inventory, Order, Warehouse
Inventory 5 5 → Book
MaintenanceLog 7 3 → Book, SystemAdmin
Manager 5 6 → Customer, Book, Order
SystemAdmin 4 4 → Book, MaintenanceLog
Metrics 10 9 → PerformanceMetric, OrderMetrics, SystemMetrics
Order 11 7 → Customer, Book, OrderProcessor, Warehouse
Payment 7 4 → Customer, Order
PerishableBook 9 8 → Book
Route 5 5 → Location, Coordinates
Transaction 8 4 → Customer
NotificationSystem 7 10 → EmailNotification, SMSNotification, PushNotification
StorageUnit 8 7 → StorageZone, Shelf
TrackingSystem 2 5 → Book, Location
Bundle 9 6 → Book
Bookstore 6 7 → Customer, Customer, Book, Order
Warehouse 3 4 → Book
Cart 4 4 → Book
Book 8 6 → Customer, Location
Warehouse 7 5 → Location, Book
StorageManager 6 6 → AuthService, Warehouse, Book, StorageUnit
OrderTracker 2 4 →
SalesAnalyzer 4 7 →
ReportGenerator 2 4 →
PerformanceMetric 4 3 →
OrderMetrics 4 3 →
SystemMetrics 3 3 →
EmailNotification 2 4 →
SMSNotification 3 4 →
PushNotification 2 2 →
StorageZone 5 2 →
Shelf 4 1 →

Exceptions (12):
BookCatalogException 1 1 →
InvalidPaymentException 0 0 →
InvalidCustomerDataException 0 0 →
OrderNotFoundException 0 0 →
InvalidOrderDataException 0 0 →
InvalidBookDataException 0 0 →
BookOutOfStockException 0 0 →
InsufficientInventoryException 0 0 →
BookNotAvailableException 0 0 →
CustomerNotAvailableException 0 0 →
InvalidUserCredentialsException 0 0 →

Поля: 193

Поведения: 175

Ассоциации: 67

Исключения: 12