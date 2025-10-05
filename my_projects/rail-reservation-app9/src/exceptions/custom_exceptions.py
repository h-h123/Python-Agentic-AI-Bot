class RailwayReservationError(Exception):
    """Base exception class for all railway reservation system errors."""
    pass

class TrainNotFoundError(RailwayReservationError):
    """Raised when a train with the specified ID is not found."""
    def __init__(self, train_id: str):
        self.train_id = train_id
        super().__init__(f"Train with ID '{train_id}' not found.")

class SeatNotAvailableError(RailwayReservationError):
    """Raised when attempting to book an already booked seat."""
    def __init__(self, train_id: str, seat_number: int):
        self.train_id = train_id
        self.seat_number = seat_number
        super().__init__(f"Seat {seat_number} on train {train_id} is not available.")

class InvalidSeatNumberError(RailwayReservationError):
    """Raised when an invalid seat number is provided."""
    def __init__(self, seat_number: int, max_seats: int):
        self.seat_number = seat_number
        self.max_seats = max_seats
        super().__init__(f"Invalid seat number {seat_number}. Must be between 1 and {max_seats}.")

class BookingNotFoundError(RailwayReservationError):
    """Raised when a booking with the specified ID is not found."""
    def __init__(self, booking_id: str):
        self.booking_id = booking_id
        super().__init__(f"Booking with ID '{booking_id}' not found.")

class PassengerNotFoundError(RailwayReservationError):
    """Raised when a passenger with the specified ID is not found."""
    def __init__(self, passenger_id: str):
        self.passenger_id = passenger_id
        super().__init__(f"Passenger with ID '{passenger_id}' not found.")

class TrainAlreadyExistsError(RailwayReservationError):
    """Raised when attempting to add a train that already exists."""
    def __init__(self, train_id: str):
        self.train_id = train_id
        super().__init__(f"Train with ID '{train_id}' already exists.")

class PassengerAlreadyExistsError(RailwayReservationError):
    """Raised when attempting to create a passenger that already exists."""
    def __init__(self, passenger_id: str):
        self.passenger_id = passenger_id
        super().__init__(f"Passenger with ID '{passenger_id}' already exists.")

class BookingAlreadyCancelledError(RailwayReservationError):
    """Raised when attempting to cancel an already cancelled booking."""
    def __init__(self, booking_id: str):
        self.booking_id = booking_id
        super().__init__(f"Booking with ID '{booking_id}' is already cancelled.")

class InvalidTrainCapacityError(RailwayReservationError):
    """Raised when an invalid train capacity is provided."""
    def __init__(self, capacity: int, max_allowed: int):
        self.capacity = capacity
        self.max_allowed = max_allowed
        super().__init__(f"Invalid train capacity {capacity}. Maximum allowed is {max_allowed}.")

class DatabaseOperationError(RailwayReservationError):
    """Raised when a database operation fails."""
    def __init__(self, operation: str, error: str):
        self.operation = operation
        self.error = error
        super().__init__(f"Database operation '{operation}' failed: {error}")

class ValidationError(RailwayReservationError):
    """Raised when input validation fails."""
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Validation failed for {field}: {reason}")