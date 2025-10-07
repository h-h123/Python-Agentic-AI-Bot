class RailwayReservationError(Exception):
    """Base exception for railway reservation system errors"""
    pass

class TrainNotFoundError(RailwayReservationError):
    """Raised when a train is not found"""
    def __init__(self, train_id: str):
        self.train_id = train_id
        super().__init__(f"Train with ID {train_id} not found")

class SeatNotAvailableError(RailwayReservationError):
    """Raised when requested seats are not available"""
    def __init__(self, seat_class: str = None):
        if seat_class:
            super().__init__(f"No available seats in {seat_class} class")
        else:
            super().__init__("No available seats")

class BookingNotFoundError(RailwayReservationError):
    """Raised when a booking is not found"""
    def __init__(self, booking_id: str):
        self.booking_id = booking_id
        super().__init__(f"Booking with ID {booking_id} not found")

class InvalidSeatClassError(RailwayReservationError):
    """Raised when an invalid seat class is provided"""
    def __init__(self, seat_class: str, valid_classes: list):
        self.seat_class = seat_class
        self.valid_classes = valid_classes
        super().__init__(f"Invalid seat class: {seat_class}. Valid classes are: {', '.join(valid_classes)}")

class PaymentProcessingError(RailwayReservationError):
    """Raised when payment processing fails"""
    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(message)

class InvalidPassengerDataError(RailwayReservationError):
    """Raised when passenger data is invalid"""
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Invalid {field}: {message}")

class DuplicateTrainError(RailwayReservationError):
    """Raised when trying to add a train with duplicate ID"""
    def __init__(self, train_id: str):
        self.train_id = train_id
        super().__init__(f"Train with ID {train_id} already exists")

class DatabaseOperationError(RailwayReservationError):
    """Raised when a database operation fails"""
    def __init__(self, operation: str, message: str = None):
        self.operation = operation
        if message:
            super().__init__(f"Database operation '{operation}' failed: {message}")
        else:
            super().__init__(f"Database operation '{operation}' failed")

class ValidationError(RailwayReservationError):
    """Raised when data validation fails"""
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validation failed for {field}: {message}")

class AuthorizationError(RailwayReservationError):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message)

class SeatAlreadyBookedError(RailwayReservationError):
    """Raised when trying to book an already booked seat"""
    def __init__(self, seat_number: str):
        self.seat_number = seat_number
        super().__init__(f"Seat {seat_number} is already booked")

class CancellationError(RailwayReservationError):
    """Raised when booking cancellation fails"""
    def __init__(self, message: str = "Booking cancellation failed"):
        super().__init__(message)

class NotificationError(RailwayReservationError):
    """Raised when notification sending fails"""
    def __init__(self, notification_type: str, message: str = None):
        self.notification_type = notification_type
        if message:
            super().__init__(f"Failed to send {notification_type} notification: {message}")
        else:
            super().__init__(f"Failed to send {notification_type} notification")

class ConfigurationError(RailwayReservationError):
    """Raised when system configuration is invalid"""
    def __init__(self, config_key: str, message: str = None):
        self.config_key = config_key
        if message:
            super().__init__(f"Invalid configuration for {config_key}: {message}")
        else:
            super().__init__(f"Invalid configuration for {config_key}")