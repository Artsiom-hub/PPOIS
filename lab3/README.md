User 5 2 →
Customer 7 3 → LoyaltyAccount, PaymentCard
TravelAgent 6 3 → Booking

BankAccount 4 2 →
PaymentCard 7 3 → Customer, BankAccount
Transaction 7 3 → PaymentCard
PaymentGateway 2 2 → Transaction, PaymentCard

Country 4 3 → Airport
City 4 3 → Country
Destination 4 3 → City
Airport 4 2 → City

Seat 4 2 →
PassengerProfile 5 3 → Customer, Baggage
Baggage 3 1 →
Flight 7 4 → Seat, Airport

RoomType 4 1 →
Room 4 2 → RoomType
Hotel 5 3 → Room, City

Booking 5 2 → Customer
FlightBooking 8 3 → Flight, PassengerProfile, Seat
HotelBooking 7 2 → Hotel, Room
TourPackage 6 4 → Flight, Hotel
Itinerary 4 3 → FlightBooking, HotelBooking, Customer

LoyaltyProgram 3 2 →
LoyaltyAccount 4 3 → Customer, LoyaltyProgram
Coupon 4 1 →
Discount 3 1 →

CartItem 4 2 → FlightBooking, HotelBooking, TourPackage
Cart 2 3 → CartItem
SearchCriteria 4 1 → Airport
RecommendationEngine 1 2 → Destination, Customer

Notification 5 2 → User
EmailNotification 7 1 → Notification
SMSNotification 6 1 → Notification

ChatMessage 4 1 → User
SupportTicket 5 2 → Customer, ChatMessage

Session 4 2 → User
AuthenticationService 1 3 → Session, User
TravelError 2 1 →
InvalidPasswordError 1 0 → TravelError
AuthenticationError 1 0 → TravelError
PaymentDeclinedError 1 0 → TravelError
InsufficientFundsError 1 0 → TravelError
CardNotFoundError 1 0 → TravelError
BookingNotFoundError 1 0 → TravelError
SeatUnavailableError 1 0 → TravelError
OverbookingError 1 0 → TravelError
CouponExpiredError 1 0 → TravelError
InvalidSearchCriteriaError 1 0 → TravelError
UnauthorizedActionError 1 0 → TravelError

Поля: 158
Поведения: 117
Ассоциации: 68
Исключения: 12