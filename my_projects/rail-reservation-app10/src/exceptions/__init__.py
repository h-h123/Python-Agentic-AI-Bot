class SeatNotAvailableError(Exception):
    """Exception raised when a seat is not available for booking"""
    pass

class BookingNotFoundError(Exception):
    """Exception raised when a booking is not found"""
    pass

class InvalidTrainError(Exception):
    """Exception raised when an invalid train ID is provided"""
    pass

class InvalidSeatError(Exception):
    """Exception raised when an invalid seat number is provided"""
    pass

class MaxBookingsReachedError(Exception):
    """Exception raised when a passenger has reached the maximum allowed bookings"""
    pass

class BookingExpiredError(Exception):
    """Exception raised when trying to use an expired booking"""
    pass

__all__ = [
    "SeatNotAvailableError",
    "BookingNotFoundError",
    "InvalidTrainError",
    "InvalidSeatError",
    "MaxBookingsReachedError",
    "BookingExpiredError"
]