from typing import Dict, Set, List, Optional
from datetime import datetime
from src.config import config
from src.models import Train, Passenger, Booking
from src.exceptions import (
    TrainNotFoundError, SeatNotAvailableError, InvalidSeatNumberError,
    BookingNotFoundError, PassengerNotFoundError, TrainAlreadyExistsError,
    PassengerAlreadyExistsError, BookingAlreadyCancelledError,
    InvalidTrainCapacityError
)

def validate_train_id(train_id: str) -> bool:
    """Validate train ID format."""
    return bool(train_id) and len(train_id) <= 20

def validate_seat_number(seat_number: int, max_seats: int) -> bool:
    """Validate seat number is within valid range."""
    return 1 <= seat_number <= max_seats

def generate_booking_id() -> str:
    """Generate a unique booking ID."""
    booking_id = f"B{config.next_booking_id}"
    config.next_booking_id += 1
    return booking_id

def get_available_seats(train_id: str) -> Set[int]:
    """Get all available seats for a train."""
    train = config.trains.get(train_id)
    if not train:
        raise TrainNotFoundError(train_id)

    all_seats = set(range(1, train.total_seats + 1))
    return all_seats - train.booked_seats

def get_train_occupancy(train_id: str) -> float:
    """Calculate train occupancy percentage."""
    train = config.trains.get(train_id)
    if not train or train.total_seats == 0:
        return 0.0
    return (len(train.booked_seats) / train.total_seats) * 100

def validate_booking(booking_id: str) -> bool:
    """Check if a booking exists and is active."""
    if booking_id not in config.bookings:
        raise BookingNotFoundError(booking_id)
    if not config.bookings[booking_id].is_active:
        raise BookingAlreadyCancelledError(booking_id)
    return True

__all__ = [
    'validate_train_id',
    'validate_seat_number',
    'generate_booking_id',
    'get_available_seats',
    'get_train_occupancy',
    'validate_booking'
]