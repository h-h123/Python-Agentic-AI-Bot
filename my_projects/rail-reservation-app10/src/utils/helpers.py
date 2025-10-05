# src/utils/helpers.py

import logging
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from src.config.constants import (
    SEAT_TYPES, DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT,
    ERROR_MESSAGES, SEAT_PRICES, MAX_SEAT_NUMBER, MIN_SEAT_NUMBER
)

def generate_unique_id(prefix: str = "ID") -> str:
    """Generate a unique ID with optional prefix"""
    return f"{prefix}-{str(uuid.uuid4())[:8].upper()}"

def validate_time_format(time_str: str, time_format: str = TIME_FORMAT) -> bool:
    """Validate if a time string matches the expected format"""
    try:
        datetime.strptime(time_str, time_format)
        return True
    except ValueError:
        return False

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    digits = re.sub(r'[^\d]', '', phone)
    return len(digits) >= 10 and len(digits) <= 15

def setup_logging(log_file: str = "railway_reservation.log", level: str = "INFO") -> logging.Logger:
    """Set up logging configuration"""
    logger = logging.getLogger("railway_reservation")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def calculate_booking_price(seat_type: str, base_price: float = 25.0) -> float:
    """Calculate booking price based on seat type"""
    return SEAT_PRICES.get(seat_type, base_price)

def format_currency(amount: float) -> str:
    """Format currency value"""
    return f"${amount:.2f}"

def parse_datetime(datetime_str: str, format: str = DATETIME_FORMAT) -> datetime:
    """Parse datetime string to datetime object"""
    return datetime.strptime(datetime_str, format)

def format_datetime(dt: datetime, format: str = DATETIME_FORMAT) -> str:
    """Format datetime object to string"""
    return dt.strftime(format)

def get_current_datetime() -> datetime:
    """Get current datetime"""
    return datetime.now()

def generate_booking_expiry(hours: int = 24) -> datetime:
    """Generate booking expiry datetime"""
    return datetime.now() + timedelta(hours=hours)

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    return re.sub(r'[^\w\s-]', '', input_str).strip()

def validate_seat_number(seat_number: int) -> bool:
    """Validate seat number range"""
    return MIN_SEAT_NUMBER <= seat_number <= MAX_SEAT_NUMBER

def validate_seat_type(seat_type: str) -> bool:
    """Validate seat type"""
    return seat_type in SEAT_TYPES.values()

def get_seat_price(seat_type: str) -> float:
    """Get price for a specific seat type"""
    return SEAT_PRICES.get(seat_type, SEAT_PRICES[SEAT_TYPES["STANDARD"]])

def format_train_schedule(train_data: Dict[str, Any]) -> str:
    """Format train schedule information for display"""
    return (f"Train {train_data['train_id']}: {train_data['name']} "
            f"({train_data['source']} to {train_data['destination']}), "
            f"Departs: {train_data['departure_time']}, Arrives: {train_data['arrival_time']}")

def format_booking_details(booking_data: Dict[str, Any]) -> str:
    """Format booking details for display"""
    return (f"Booking {booking_data['booking_id']}: "
            f"Train {booking_data['train_id']}, Seat {booking_data['seat_number']} "
            f"({booking_data['seat_type']}), Passenger: {booking_data['passenger_name']}, "
            f"Status: {booking_data['status']}, Price: {format_currency(booking_data['price'])}")

def create_seat_map(seats: List[Dict[str, Any]]) -> Dict[int, str]:
    """Create a seat map dictionary from seat data"""
    return {seat['seat_number']: seat['status'] for seat in seats}

def validate_train_route(source: str, destination: str) -> bool:
    """Validate train route"""
    return (source and destination and
            isinstance(source, str) and
            isinstance(destination, str) and
            source.strip().lower() != destination.strip().lower())