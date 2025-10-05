from typing import Optional, Union
from datetime import datetime
import re
from src.config.constants import (
    SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED, SEAT_STATUS_MAINTENANCE,
    SEAT_TYPES, MIN_SEAT_NUMBER, MAX_SEAT_NUMBER,
    DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT,
    ERROR_MESSAGES
)

class InputValidator:
    @staticmethod
    def validate_train_id(train_id: str) -> bool:
        """Validate train ID format"""
        if not train_id or not isinstance(train_id, str):
            return False
        return len(train_id) >= 3 and train_id[0].isalpha()

    @staticmethod
    def validate_seat_number(seat_number: int) -> bool:
        """Validate seat number range"""
        return MIN_SEAT_NUMBER <= seat_number <= MAX_SEAT_NUMBER

    @staticmethod
    def validate_seat_status(status: str) -> bool:
        """Validate seat status"""
        return status in [SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED, SEAT_STATUS_MAINTENANCE]

    @staticmethod
    def validate_seat_type(seat_type: str) -> bool:
        """Validate seat type"""
        return seat_type in SEAT_TYPES.values()

    @staticmethod
    def validate_time(time_str: str, time_format: str = TIME_FORMAT) -> bool:
        """Validate time format"""
        try:
            datetime.strptime(time_str, time_format)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_date(date_str: str, date_format: str = DATE_FORMAT) -> bool:
        """Validate date format"""
        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_datetime(datetime_str: str, datetime_format: str = DATETIME_FORMAT) -> bool:
        """Validate datetime format"""
        try:
            datetime.strptime(datetime_str, datetime_format)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_passenger_name(name: str) -> bool:
        """Validate passenger name"""
        if not name or not isinstance(name, str):
            return False
        return len(name.strip()) >= 2 and bool(re.match(r'^[a-zA-Z\s\-]+$', name.strip()))

    @staticmethod
    def validate_booking_id(booking_id: str) -> bool:
        """Validate booking ID format"""
        if not booking_id or not isinstance(booking_id, str):
            return False
        return len(booking_id) >= 5 and '-' in booking_id

    @staticmethod
    def validate_positive_number(value: Union[int, float]) -> bool:
        """Validate positive number"""
        return isinstance(value, (int, float)) and value > 0

    @staticmethod
    def validate_train_capacity(capacity: int) -> bool:
        """Validate train capacity"""
        return isinstance(capacity, int) and 10 <= capacity <= 200

class BusinessRuleValidator:
    @staticmethod
    def can_book_seat(seat_status: str) -> bool:
        """Check if seat can be booked"""
        return seat_status == SEAT_STATUS_AVAILABLE

    @staticmethod
    def can_cancel_booking(booking_status: str) -> bool:
        """Check if booking can be cancelled"""
        return booking_status == "Confirmed"

    @staticmethod
    def is_valid_train_route(source: str, destination: str) -> bool:
        """Check if train route is valid"""
        return (source and destination and
                isinstance(source, str) and
                isinstance(destination, str) and
                source.lower() != destination.lower())

    @staticmethod
    def is_valid_booking_expiry(expiry_time: str) -> bool:
        """Check if booking expiry time is valid"""
        try:
            expiry = datetime.strptime(expiry_time, DATETIME_FORMAT)
            return expiry > datetime.now()
        except ValueError:
            return False

def validate_and_sanitize_input(input_str: str, max_length: int = 100) -> str:
    """Validate and sanitize user input"""
    if not input_str or not isinstance(input_str, str):
        raise ValueError("Input must be a non-empty string")

    sanitized = re.sub(r'[^\w\s\-.,@]', '', input_str.strip())
    if len(sanitized) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters")

    return sanitized