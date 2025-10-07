import re
from datetime import datetime
from typing import Optional, Dict, List, Union
from src.config.settings import settings
from src.models.train import Seat

def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    if not phone:
        return False
    # Remove all non-digit characters
    digits = re.sub(r'[^\d]', '', phone)
    # Basic validation: 8-15 digits, optionally with country code
    return 8 <= len(digits) <= 15

def validate_passenger_name(name: str) -> bool:
    """Validate passenger name format."""
    if not name or len(name.strip()) < 2:
        return False
    # Allow letters, spaces, hyphens, and apostrophes
    pattern = r'^[a-zA-Z\s\-\']+$'
    return bool(re.match(pattern, name.strip()))

def validate_train_id(train_id: str) -> bool:
    """Validate train ID format."""
    if not train_id:
        return False
    # Typical format: letter followed by numbers (e.g., T101, EXP202)
    pattern = r'^[A-Za-z]{1,3}\d{2,4}$'
    return bool(re.match(pattern, train_id))

def validate_booking_id(booking_id: str) -> bool:
    """Validate booking ID format (UUID)."""
    if not booking_id:
        return False
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, booking_id.lower()))

def validate_seat_class(seat_class: str) -> bool:
    """Validate seat class against allowed values."""
    if not seat_class:
        return False
    return seat_class.lower() in [cls.lower() for cls in settings.default_seat_classes]

def validate_payment_method(payment_method: str) -> bool:
    """Validate payment method."""
    if not payment_method:
        return False
    valid_methods = ["credit_card", "debit_card", "paypal", "bank_transfer", "mobile_wallet"]
    return payment_method.lower() in valid_methods

def validate_seat_availability(seats: List[Seat], seat_class: Optional[str] = None) -> bool:
    """Check if seats are available, optionally filtered by class."""
    if seat_class:
        seats = [seat for seat in seats if seat.seat_class.lower() == seat_class.lower()]
    return any(not seat.is_booked for seat in seats)

def validate_date_format(date_str: str, date_format: str = "%Y-%m-%d") -> bool:
    """Validate if a string matches the expected date format."""
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False

def validate_time_format(time_str: str, time_format: str = "%H:%M") -> bool:
    """Validate if a string matches the expected time format."""
    try:
        datetime.strptime(time_str, time_format)
        return True
    except ValueError:
        return False

def validate_departure_time(departure_time: datetime) -> bool:
    """Validate that departure time is in the future."""
    return departure_time > datetime.now()

def validate_positive_number(value: Union[int, float]) -> bool:
    """Validate that a number is positive."""
    return value is not None and value > 0

def validate_price(price: float, seat_class: str) -> bool:
    """Validate price against seat class minimum prices."""
    if not validate_positive_number(price):
        return False

    if seat_class.lower() == "economy":
        return price >= float(settings.price_economy)
    elif seat_class.lower() == "business":
        return price >= float(settings.price_business)
    return False

def validate_booking_data(
    train_id: str,
    passenger_name: str,
    seat_class: str,
    email: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict[str, str]:
    """Validate all booking data and return errors if any."""
    errors = {}

    if not validate_train_id(train_id):
        errors["train_id"] = "Invalid train ID format"

    if not validate_passenger_name(passenger_name):
        errors["passenger_name"] = "Passenger name must be at least 2 characters and contain only letters, spaces, hyphens, or apostrophes"

    if not validate_seat_class(seat_class):
        errors["seat_class"] = f"Seat class must be one of: {', '.join(settings.default_seat_classes)}"

    if email and not validate_email(email):
        errors["email"] = "Invalid email format"

    if phone and not validate_phone(phone):
        errors["phone"] = "Invalid phone number format"

    return errors

def validate_train_data(
    train_id: str,
    name: str,
    source: str,
    destination: str,
    departure_time: datetime,
    total_seats: int
) -> Dict[str, str]:
    """Validate all train data and return errors if any."""
    errors = {}

    if not validate_train_id(train_id):
        errors["train_id"] = "Invalid train ID format"

    if not name or len(name.strip()) < 2:
        errors["name"] = "Train name must be at least 2 characters"

    if not source or len(source.strip()) < 2:
        errors["source"] = "Source must be at least 2 characters"

    if not destination or len(destination.strip()) < 2:
        errors["destination"] = "Destination must be at least 2 characters"

    if source.strip().lower() == destination.strip().lower():
        errors["route"] = "Source and destination cannot be the same"

    if not validate_departure_time(departure_time):
        errors["departure_time"] = "Departure time must be in the future"

    if not validate_positive_number(total_seats):
        errors["total_seats"] = "Total seats must be a positive number"

    if total_seats > int(settings.max_seats_per_train):
        errors["total_seats"] = f"Total seats cannot exceed {settings.max_seats_per_train}"

    return errors