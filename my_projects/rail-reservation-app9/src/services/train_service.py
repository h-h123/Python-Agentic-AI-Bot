from typing import Dict, Optional, List, Set
from datetime import datetime
from src.config import config
from src.models import Train, Passenger, Booking
from src.config.constants import (
    TRAIN_EXISTS, TRAIN_NOT_FOUND, BOOKING_FAILED,
    PASSENGER_EXISTS, INVALID_SEAT_NUMBER, TRAIN_ADDED,
    BOOKING_SUCCESS, BOOKING_CANCEL_SUCCESS, BOOKING_NOT_FOUND
)

def add_train(train_id: str, name: str, total_seats: int) -> bool:
    """Add a new train to the railway system."""
    if train_id in config.trains:
        print(TRAIN_EXISTS)
        return False

    if total_seats <= 0 or total_seats > config.MAX_SEATS_PER_TRAIN:
        print(INVALID_SEAT_NUMBER)
        return False

    config.trains[train_id] = Train(
        train_id=train_id,
        name=name,
        total_seats=total_seats
    )
    print(TRAIN_ADDED)
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

    print(BOOKING_SUCCESS)
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

    print(BOOKING_CANCEL_SUCCESS)
    return True

def get_train_details(train_id: str) -> Optional[Train]:
    """Get details of a specific train."""
    return config.trains.get(train_id)

def get_passenger_bookings(passenger_id: str) -> List[Booking]:
    """Get all active bookings for a passenger."""
    if passenger_id not in config.passengers:
        print(BOOKING_NOT_FOUND)
        return []

    passenger = config.passengers[passenger_id]
    active_bookings = []

    for booking_id in passenger.booking_ids:
        booking = config.bookings.get(booking_id)
        if booking and booking.is_active:
            active_bookings.append(booking)

    return active_bookings

def get_available_seats(train_id: str) -> Set[int]:
    """Get all available seats for a train."""
    train = config.trains.get(train_id)
    if not train:
        return set()

    all_seats = set(range(1, train.total_seats + 1))
    return all_seats - train.booked_seats

def get_train_occupancy(train_id: str) -> float:
    """Get the occupancy percentage of a train."""
    train = config.trains.get(train_id)
    if not train or train.total_seats == 0:
        return 0.0

    return (len(train.booked_seats) / train.total_seats) * 100