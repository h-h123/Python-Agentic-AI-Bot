ERROR_ERROR = "An unexpected error occurred. Please try again."

# Booking related constants
BOOKING_SUCCESS = "Seat booked successfully!"
BOOKING_FAILED = "Booking failed. Seat may be unavailable or invalid."
BOOKING_CANCEL_SUCCESS = "Booking cancelled successfully!"
BOOKING_CANCEL_FAILED = "Cancellation failed. Invalid booking ID."
BOOKING_NOT_FOUND = "No bookings found for this passenger."

# Train related constants
TRAIN_ADDED = "Train added successfully!"
TRAIN_EXISTS = "Train with this ID already exists."
TRAIN_NOT_FOUND = "Train not found."
TRAIN_SEATS_FULL = "All seats on this train are booked."

# Passenger related constants
PASSENGER_CREATED = "Passenger record created."
PASSENGER_EXISTS = "Passenger with this ID already exists."

# Validation constants
INVALID_INPUT = "Invalid input. Please try again."
INVALID_TRAIN_ID = "Invalid train ID format."
INVALID_SEAT_NUMBER = "Seat number must be a positive integer."
INVALID_CHOICE = "Invalid choice. Please try again."

# System constants
MAX_SEATS_PER_TRAIN = 100
DEFAULT_TRAIN_CAPACITY = 50
BOOKING_EXPIRY_DAYS = 30
SYSTEM_EXIT = "Exiting the system. Goodbye!"

# Database constants
DB_URL = "sqlite:///railway_reservation.db"
DB_ECHO = False

# Logging constants
LOG_LEVEL = "INFO"
LOG_FILE = "railway_reservation.log"

# API constants
API_HOST = "127.0.0.1"
API_PORT = 5000
API_DEBUG = False