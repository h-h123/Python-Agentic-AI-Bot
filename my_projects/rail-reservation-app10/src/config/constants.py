# src/config/constants.py

SEAT_STATUS_AVAILABLE = "Available"
SEAT_STATUS_BOOKED = "Booked"
SEAT_STATUS_MAINTENANCE = "Maintenance"

BOOKING_STATUS_CONFIRMED = "Confirmed"
BOOKING_STATUS_CANCELLED = "Cancelled"

SEAT_TYPES = {
    "STANDARD": "Standard",
    "BUSINESS": "Business",
    "FIRST_CLASS": "First Class"
}

SEAT_PRICES = {
    "STANDARD": 25.00,
    "BUSINESS": 50.00,
    "FIRST_CLASS": 100.00
}

MAX_BOOKINGS_PER_PASSENGERS = 5
BOOKING_EXPIRY_HOURS = 24

DEFAULT_TRAIN_CAPACITY = 50
MIN_SEAT_NUMBER = 1
MAX_SEAT_NUMBER = 50

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

ERROR_MESSAGES = {
    "seat_not_available": "The requested seat is not available for booking",
    "booking_not_found": "No booking found with the provided ID",
    "invalid_train": "Invalid train ID provided",
    "invalid_seat": "Invalid seat number provided",
    "max_bookings_reached": "Maximum bookings limit reached for this passenger",
    "booking_expired": "This booking has already expired"
}