from src.config.constants import ERROR_MESSAGES

class SeatNotAvailableError(Exception):
    """Exception raised when a seat is not available for booking"""
    def __init__(self, message=None):
        self.message = message or ERROR_MESSAGES["seat_not_available"]
        super().__init__(self.message)

class BookingNotFoundError(Exception):
    """Exception raised when a booking is not found"""
    def __init__(self, message=None):
        self.message = message or ERROR_MESSAGES["booking_not_found"]
        super().__init__(self.message)

class InvalidTrainError(Exception):
    """Exception raised when an invalid train ID is provided"""
    def __init__(self, message=None):
        self.message = message or ERROR_MESSAGES["invalid_train"]
        super().__init__(self.message)

class InvalidSeatError(Exception):
    """Exception raised when an invalid seat number is provided"""
    def __init__(self, message=None):
        self.message = message or ERROR_MESSAGES["invalid_seat"]
        super().__init__(self.message)

class MaxBookingsReachedError(Exception):
    """Exception raised when a passenger has reached the maximum allowed bookings"""
    def __init__(self, message=None):
        self.message = message or ERROR_MESSAGES["max_bookings_reached"]
        super().__init__(self.message)

class BookingExpiredError(Exception):
    """Exception raised when trying to use an expired booking"""
    def __init__(self, message=None):
        self.message = message or ERROR_MESSAGES["booking_expired"]
        super().__init__(self.message)

class DatabaseConnectionError(Exception):
    """Exception raised when there's an issue connecting to the database"""
    def __init__(self, message="Failed to connect to the database"):
        self.message = message
        super().__init__(self.message)

class TrainCapacityExceededError(Exception):
    """Exception raised when trying to add more seats than a train's capacity"""
    def __init__(self, message="Train has reached maximum capacity"):
        self.message = message
        super().__init__(self.message)

class InvalidPassengerError(Exception):
    """Exception raised when passenger information is invalid"""
    def __init__(self, message="Invalid passenger information provided"):
        self.message = message
        super().__init__(self.message)