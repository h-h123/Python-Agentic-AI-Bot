class SeatBookingError(Exception):
    """Base exception for seat booking related errors"""
    pass

class NoAvailableSeatsError(SeatBookingError):
    """Raised when no seats are available for booking"""
    pass

class SeatAlreadyBookedError(SeatBookingError):
    """Raised when attempting to book an already booked seat"""
    def __init__(self, seat_number: int):
        self.seat_number = seat_number
        super().__init__(f"Seat {seat_number} is already booked")

class InvalidSeatNumberError(SeatBookingError):
    """Raised when an invalid seat number is provided"""
    def __init__(self, seat_number: int, max_seats: int = 100):
        self.seat_number = seat_number
        self.max_seats = max_seats
        super().__init__(f"Invalid seat number: {seat_number}. Must be between 1 and {max_seats}")

class BookingNotFoundError(SeatBookingError):
    """Raised when attempting to cancel a non-existent booking"""
    def __init__(self, seat_number: int):
        self.seat_number = seat_number
        super().__init__(f"No booking found for seat {seat_number}")

class InvalidPassengerNameError(SeatBookingError):
    """Raised when an invalid passenger name is provided"""
    pass

class TrainNotFoundError(Exception):
    """Raised when a train is not found in the system"""
    def __init__(self, train_id: str):
        self.train_id = train_id
        super().__init__(f"Train with ID {train_id} not found")

class PassengerNotFoundError(Exception):
    """Raised when a passenger is not found in the system"""
    def __init__(self, passenger_id: str):
        self.passenger_id = passenger_id
        super().__init__(f"Passenger with ID {passenger_id} not found")

class DatabaseError(Exception):
    """Base exception for database related errors"""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised when there's an issue connecting to the database"""
    pass

class DatabaseOperationError(DatabaseError):
    """Raised when a database operation fails"""
    pass