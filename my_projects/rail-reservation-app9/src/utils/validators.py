import re
from typing import Optional, Union
from datetime import datetime
from src.config.constants import (
    INVALID_TRAIN_ID, INVALID_SEAT_NUMBER,
    MAX_SEATS_PER_TRAIN, DEFAULT_TRAIN_CAPACITY
)
from src.exceptions.custom_exceptions import ValidationError

def validate_train_id(train_id: str) -> bool:
    """Validate train ID format."""
    if not train_id or len(train_id) > 20:
        raise ValidationError("train_id", INVALID_TRAIN_ID)
    return True

def validate_train_name(name: str) -> bool:
    """Validate train name format."""
    if not name or len(name) > 100:
        raise ValidationError("train_name", "Name must be 1-100 characters long")
    return True

def validate_passenger_id(passenger_id: str) -> bool:
    """Validate passenger ID format."""
    if not passenger_id or len(passenger_id) > 20:
        raise ValidationError("passenger_id", "ID must be 1-20 characters long")
    return True

def validate_passenger_name(name: str) -> bool:
    """Validate passenger name format."""
    if not name or len(name) > 100:
        raise ValidationError("passenger_name", "Name must be 1-100 characters long")
    return True

def validate_seat_number(seat_number: int, max_seats: int = MAX_SEATS_PER_TRAIN) -> bool:
    """Validate seat number is within valid range."""
    if not isinstance(seat_number, int) or seat_number < 1 or seat_number > max_seats:
        raise ValidationError("seat_number", INVALID_SEAT_NUMBER)
    return True

def validate_total_seats(total_seats: int) -> bool:
    """Validate total seats for a train."""
    if not isinstance(total_seats, int) or total_seats <= 0 or total_seats > MAX_SEATS_PER_TRAIN:
        raise ValidationError("total_seats", f"Must be between 1 and {MAX_SEATS_PER_TRAIN}")
    return True

def validate_booking_id(booking_id: str) -> bool:
    """Validate booking ID format."""
    if not booking_id or not re.match(r'^B\d+$', booking_id):
        raise ValidationError("booking_id", "Invalid booking ID format")
    return True

def validate_date_format(date_str: str, date_format: str = "%Y-%m-%d") -> bool:
    """Validate a date string matches the expected format."""
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        raise ValidationError("date", f"Must be in {date_format} format")

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("email", "Invalid email format")
    return True

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    pattern = r'^\+?[0-9\s\-\(\)]{7,}$'
    if not re.match(pattern, phone):
        raise ValidationError("phone", "Invalid phone number format")
    return True

def validate_positive_integer(value: Union[int, str], field_name: str) -> int:
    """Validate and convert a value to positive integer."""
    try:
        num = int(value)
        if num <= 0:
            raise ValidationError(field_name, "Must be a positive integer")
        return num
    except (ValueError, TypeError):
        raise ValidationError(field_name, "Must be a valid positive integer")