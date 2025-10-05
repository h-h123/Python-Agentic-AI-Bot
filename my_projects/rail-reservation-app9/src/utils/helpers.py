from typing import Dict, Set, List, Optional, Union, Any
from datetime import datetime, timedelta
import re
import uuid
from src.config import config
from src.config.constants import (
    MAX_SEATS_PER_TRAIN, DEFAULT_TRAIN_CAPACITY,
    INVALID_TRAIN_ID, INVALID_SEAT_NUMBER,
    BOOKING_EXPIRY_DAYS
)
from src.exceptions.custom_exceptions import (
    ValidationError, TrainNotFoundError,
    SeatNotAvailableError, BookingNotFoundError,
    PassengerNotFoundError, DatabaseOperationError
)

def generate_unique_id(prefix: str = "ID") -> str:
    """Generate a unique ID with optional prefix."""
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

def validate_train_id(train_id: str) -> bool:
    """Validate train ID format."""
    if not train_id or len(train_id) > 20 or not train_id.isalnum():
        raise ValidationError("train_id", INVALID_TRAIN_ID)
    return True

def validate_seat_number(seat_number: int, train: Optional[Dict] = None) -> bool:
    """Validate seat number is within valid range for a train."""
    if not isinstance(seat_number, int) or seat_number < 1:
        raise ValidationError("seat_number", INVALID_SEAT_NUMBER)

    if train:
        max_seats = train.get('total_seats', MAX_SEATS_PER_TRAIN)
        if seat_number > max_seats:
            raise ValidationError("seat_number", f"Must be between 1 and {max_seats}")
    else:
        if seat_number > MAX_SEATS_PER_TRAIN:
            raise ValidationError("seat_number", f"Must be between 1 and {MAX_SEATS_PER_TRAIN}")
    return True

def get_available_seats(train_id: str) -> Set[int]:
    """Get all available seats for a train."""
    train = config.trains.get(train_id)
    if not train:
        raise TrainNotFoundError(train_id)

    all_seats = set(range(1, train.total_seats + 1))
    return all_seats - train.booked_seats

def calculate_train_occupancy(train_id: str) -> float:
    """Calculate train occupancy percentage."""
    train = config.trains.get(train_id)
    if not train or train.total_seats == 0:
        return 0.0
    return (len(train.booked_seats) / train.total_seats) * 100

def is_booking_expired(booking_time: datetime) -> bool:
    """Check if a booking has expired based on system settings."""
    return (datetime.now() - booking_time) > timedelta(days=BOOKING_EXPIRY_DAYS)

def format_booking_details(booking: Any) -> Dict[str, Any]:
    """Format booking details for display."""
    return {
        "booking_id": booking.booking_id,
        "passenger_id": booking.passenger_id,
        "train_id": booking.train_id,
        "seat_number": booking.seat_number,
        "booking_time": booking.booking_time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Active" if booking.is_active else "Cancelled"
    }

def format_train_details(train: Any) -> Dict[str, Any]:
    """Format train details for display."""
    return {
        "train_id": train.train_id,
        "name": train.name,
        "total_seats": train.total_seats,
        "available_seats": train.total_seats - len(train.booked_seats),
        "booked_seats": sorted(train.booked_seats),
        "occupancy": calculate_train_occupancy(train.train_id)
    }

def format_passenger_details(passenger: Any) -> Dict[str, Any]:
    """Format passenger details for display."""
    return {
        "passenger_id": passenger.passenger_id,
        "name": passenger.name,
        "booking_count": len(passenger.booking_ids),
        "active_bookings": len([
            booking for booking in config.bookings.values()
            if booking.passenger_id == passenger.passenger_id and booking.is_active
        ])
    }

def validate_booking_id(booking_id: str) -> bool:
    """Validate booking ID format."""
    if not re.match(r'^B\d+$', booking_id):
        raise ValidationError("booking_id", "Invalid booking ID format")
    return True

def validate_passenger_id(passenger_id: str) -> bool:
    """Validate passenger ID format."""
    if not passenger_id or len(passenger_id) > 20:
        raise ValidationError("passenger_id", "ID must be 1-20 characters long")
    return True

def validate_train_capacity(total_seats: int) -> bool:
    """Validate train capacity is within allowed limits."""
    if not isinstance(total_seats, int) or total_seats <= 0 or total_seats > MAX_SEATS_PER_TRAIN:
        raise ValidationError("total_seats", f"Must be between 1 and {MAX_SEATS_PER_TRAIN}")
    return True

def convert_to_int(value: Union[str, int], field_name: str) -> int:
    """Convert a value to integer with validation."""
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValidationError(field_name, "Must be a valid integer")

def get_booking_by_id(booking_id: str) -> Optional[Any]:
    """Get booking by ID with validation."""
    if booking_id not in config.bookings:
        raise BookingNotFoundError(booking_id)
    return config.bookings[booking_id]

def get_passenger_by_id(passenger_id: str) -> Optional[Any]:
    """Get passenger by ID with validation."""
    if passenger_id not in config.passengers:
        raise PassengerNotFoundError(passenger_id)
    return config.passengers[passenger_id]

def get_train_by_id(train_id: str) -> Optional[Any]:
    """Get train by ID with validation."""
    if train_id not in config.trains:
        raise TrainNotFoundError(train_id)
    return config.trains[train_id]

def check_seat_availability(train_id: str, seat_number: int) -> bool:
    """Check if a seat is available on a train."""
    train = get_train_by_id(train_id)
    if not train.is_seat_available(seat_number):
        raise SeatNotAvailableError(train_id, seat_number)
    return True