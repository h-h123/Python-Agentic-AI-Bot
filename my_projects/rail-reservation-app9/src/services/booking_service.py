from typing import Dict, Optional, List
from datetime import datetime
from src.config import config
from src.models import Train, Passenger, Booking
from src.config.constants import (
    TRAIN_EXISTS, TRAIN_NOT_FOUND, BOOKING_FAILED,
    PASSENGER_EXISTS, INVALID_SEAT_NUMBER
)

def add_train(train_id: str, name: str, total_seats: int) -> bool:
    """Add a new train to the system."""
    if train_id in config.trains:
        print(TRAIN_EXISTS)
        return False

    if total_seats <= 0:
        print(INVALID_SEAT_NUMBER)
        return False

    config.trains[train_id] = Train(
        train_id=train_id,
        name=name,
        total_seats=total_seats
    )
    return True

def book_seat(passenger_id: str, passenger_name: str, train_id: str, seat_number: int) -> Optional[Booking]:
    """Book a seat on a train for a passenger."""
    if train_id not in config.trains:
        print(TRAIN_NOT_FOUND)
        return None

    train = config.trains[train_id]

    if not train.is_seat_available(seat_number):
        print(BOOKING_FAILED)
        return None

    # Create or update passenger
    if passenger_id not in config.passengers:
        config.passengers[passenger_id] = Passenger(
            passenger_id=passenger_id,
            name=passenger_name
        )
    else:
        if config.passengers[passenger_id].name != passenger_name:
            config.passengers[passenger_id].name = passenger_name

    # Create booking
    booking_id = f"B{config.next_booking_id}"
    config.next_booking_id += 1

    booking = Booking.create_booking(
        passenger_id=passenger_id,
        train_id=train_id,
        seat_number=seat_number,
        booking_id=booking_id
    )

    # Update train and passenger records
    train.book_seat(seat_number)
    config.passengers[passenger_id].add_booking(booking_id)
    config.bookings[booking_id] = booking

    return booking

def cancel_booking(booking_id: str) -> bool:
    """Cancel an existing booking."""
    if booking_id not in config.bookings:
        return False

    booking = config.bookings[booking_id]
    if not booking.is_active:
        return False

    train = config.trains.get(booking.train_id)
    passenger = config.passengers.get(booking.passenger_id)

    if not train or not passenger:
        return False

    # Update records
    train.cancel_seat(booking.seat_number)
    passenger.remove_booking(booking_id)
    booking.cancel()

    return True

def get_train_details(train_id: str) -> Optional[Train]:
    """Get details of a specific train."""
    return config.trains.get(train_id)

def get_passenger_bookings(passenger_id: str) -> List[Booking]:
    """Get all active bookings for a passenger."""
    if passenger_id not in config.passengers:
        return []

    passenger = config.passengers[passenger_id]
    active_bookings = []

    for booking_id in passenger.booking_ids:
        booking = config.bookings.get(booking_id)
        if booking and booking.is_active:
            active_bookings.append(booking)

    return active_bookings