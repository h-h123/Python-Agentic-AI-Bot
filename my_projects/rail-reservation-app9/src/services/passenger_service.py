from typing import Dict, Optional, List
from src.config import config
from src.models import Passenger, Booking
from src.config.constants import PASSENGER_EXISTS, PASSENGER_CREATED

def create_passenger(passenger_id: str, name: str) -> bool:
    """Create a new passenger in the system."""
    if passenger_id in config.passengers:
        print(PASSENGER_EXISTS)
        return False

    config.passengers[passenger_id] = Passenger(
        passenger_id=passenger_id,
        name=name
    )
    print(PASSENGER_CREATED)
    return True

def get_passenger(passenger_id: str) -> Optional[Passenger]:
    """Get passenger details by ID."""
    return config.passengers.get(passenger_id)

def update_passenger_name(passenger_id: str, new_name: str) -> bool:
    """Update a passenger's name."""
    passenger = config.passengers.get(passenger_id)
    if not passenger:
        return False

    passenger.name = new_name
    return True

def get_all_passenger_bookings(passenger_id: str) -> List[Booking]:
    """Get all bookings (active and inactive) for a passenger."""
    if passenger_id not in config.passengers:
        return []

    passenger = config.passengers[passenger_id]
    all_bookings = []

    for booking_id in passenger.booking_ids:
        booking = config.bookings.get(booking_id)
        if booking:
            all_bookings.append(booking)

    return all_bookings

def passenger_has_active_bookings(passenger_id: str) -> bool:
    """Check if a passenger has any active bookings."""
    if passenger_id not in config.passengers:
        return False

    passenger = config.passengers[passenger_id]
    for booking_id in passenger.booking_ids:
        booking = config.bookings.get(booking_id)
        if booking and booking.is_active:
            return True

    return False

def get_passenger_booking_history(passenger_id: str) -> List[Booking]:
    """Get complete booking history for a passenger."""
    return get_all_passenger_bookings(passenger_id)