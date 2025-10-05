from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import uuid
import re

def generate_unique_id(prefix: str = "ID") -> str:
    """Generate a unique ID with optional prefix"""
    return f"{prefix}-{str(uuid.uuid4())[:8].upper()}"

def validate_time_format(time_str: str, time_format: str = "%H:%M") -> bool:
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
    # Remove all non-digit characters
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
    price_multipliers = {
        "Standard": 1.0,
        "Business": 2.0,
        "First Class": 4.0
    }
    return base_price * price_multipliers.get(seat_type, 1.0)

def format_currency(amount: float) -> str:
    """Format currency value"""
    return f"${amount:.2f}"

def parse_datetime(datetime_str: str, format: str = "%Y-%m-%d %H:%M") -> datetime:
    """Parse datetime string to datetime object"""
    return datetime.strptime(datetime_str, format)

def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M") -> str:
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

__all__ = [
    "generate_unique_id",
    "validate_time_format",
    "validate_email",
    "validate_phone",
    "setup_logging",
    "calculate_booking_price",
    "format_currency",
    "parse_datetime",
    "format_datetime",
    "get_current_datetime",
    "generate_booking_expiry",
    "sanitize_input"
]