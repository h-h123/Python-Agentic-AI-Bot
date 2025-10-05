import re
from typing import Optional, Union, Dict, Any

class Validators:
    @staticmethod
    def validate_passenger_name(name: str) -> bool:
        """Validate passenger name (letters, spaces, hyphens, apostrophes only)"""
        if not name or not name.strip():
            return False
        return bool(re.fullmatch(r'^[a-zA-Z\s\-\']+$', name.strip()))

    @staticmethod
    def validate_seat_number(seat_number: int, max_seats: int = 100) -> bool:
        """Validate seat number is within valid range"""
        return isinstance(seat_number, int) and 1 <= seat_number <= max_seats

    @staticmethod
    def validate_train_id(train_id: str) -> bool:
        """Validate train ID format (alphanumeric with optional hyphens)"""
        return bool(re.fullmatch(r'^[A-Za-z0-9\-]+$', train_id)) if train_id else False

    @staticmethod
    def validate_email(email: Optional[str]) -> bool:
        """Validate email format if provided"""
        if not email:
            return True
        return bool(re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

    @staticmethod
    def validate_phone(phone: Optional[str]) -> bool:
        """Validate phone number format if provided"""
        if not phone:
            return True
        return bool(re.fullmatch(r'^\+?[0-9\s\-()]{7,}$', phone))

    @staticmethod
    def validate_booking_data(data: Dict[str, Any]) -> Dict[str, Union[bool, str]]:
        """Validate complete booking data"""
        errors = {}

        if 'passenger_name' not in data or not Validators.validate_passenger_name(data['passenger_name']):
            errors['passenger_name'] = "Invalid passenger name"

        if 'seat_number' in data and not Validators.validate_seat_number(data['seat_number']):
            errors['seat_number'] = "Invalid seat number"

        if 'train_id' in data and not Validators.validate_train_id(data['train_id']):
            errors['train_id'] = "Invalid train ID"

        if 'email' in data and not Validators.validate_email(data['email']):
            errors['email'] = "Invalid email format"

        if 'phone' in data and not Validators.validate_phone(data['phone']):
            errors['phone'] = "Invalid phone number format"

        return {'is_valid': not bool(errors), 'errors': errors}