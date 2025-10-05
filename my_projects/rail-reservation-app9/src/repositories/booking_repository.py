from typing import Dict, Optional, List, Set
from datetime import datetime
from src.config import config
from src.models import Train, Passenger, Booking

class BookingRepository:
    @staticmethod
    def create_booking(passenger_id: str, passenger_name: str, train_id: str, seat_number: int) -> Optional[Booking]:
        """Create a new booking in the repository."""
        if train_id not in config.trains:
            return None

        train = config.trains[train_id]
        if not train.is_seat_available(seat_number):
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

    @staticmethod
    def cancel_booking(booking_id: str) -> bool:
        """Cancel an existing booking in the repository."""
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

    @staticmethod
    def get_booking(booking_id: str) -> Optional[Booking]:
        """Get a booking by its ID."""
        return config.bookings.get(booking_id)

    @staticmethod
    def get_active_bookings() -> List[Booking]:
        """Get all active bookings in the system."""
        return [booking for booking in config.bookings.values() if booking.is_active]

    @staticmethod
    def get_passenger_bookings(passenger_id: str) -> List[Booking]:
        """Get all active bookings for a specific passenger."""
        if passenger_id not in config.passengers:
            return []

        passenger = config.passengers[passenger_id]
        active_bookings = []

        for booking_id in passenger.booking_ids:
            booking = config.bookings.get(booking_id)
            if booking and booking.is_active:
                active_bookings.append(booking)

        return active_bookings

    @staticmethod
    def get_bookings_by_train(train_id: str) -> List[Booking]:
        """Get all active bookings for a specific train."""
        return [booking for booking in config.bookings.values()
                if booking.is_active and booking.train_id == train_id]