class TrainNotFoundError(Exception):
    """Raised when a train with the specified ID is not found."""
    pass

class SeatNotAvailableError(Exception):
    """Raised when attempting to book an already booked seat."""
    pass

class InvalidSeatNumberError(Exception):
    """Raised when an invalid seat number is provided."""
    pass

class BookingNotFoundError(Exception):
    """Raised when a booking with the specified ID is not found."""
    pass

class PassengerNotFoundError(Exception):
    """Raised when a passenger with the specified ID is not found."""
    pass

class TrainAlreadyExistsError(Exception):
    """Raised when attempting to add a train that already exists."""
    pass

class PassengerAlreadyExistsError(Exception):
    """Raised when attempting to create a passenger that already exists."""
    pass

class BookingAlreadyCancelledError(Exception):
    """Raised when attempting to cancel an already cancelled booking."""
    pass

class InvalidTrainCapacityError(Exception):
    """Raised when an invalid train capacity is provided."""
    pass

__all__ = [
    'TrainNotFoundError',
    'SeatNotAvailableError',
    'InvalidSeatNumberError',
    'BookingNotFoundError',
    'PassengerNotFoundError',
    'TrainAlreadyExistsError',
    'PassengerAlreadyExistsError',
    'BookingAlreadyCancelledError',
    'InvalidTrainCapacityError'
]