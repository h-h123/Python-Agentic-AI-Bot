# src/repositories/booking_repository.py

from typing import Dict, List, Optional
from src.models import Booking
from src.exceptions import BookingNotFoundError
from src.config.constants import BOOKING_STATUS_CONFIRMED, BOOKING_STATUS_CANCELLED

class BookingRepository:
    def __init__(self):
        self._bookings: Dict[str, Booking] = {}

    def save(self, booking: Booking) -> Booking:
        """Save a booking to the repository"""
        self._bookings[booking.booking_id] = booking
        return booking

    def find_by_id(self, booking_id: str) -> Optional[Booking]:
        """Find a booking by its ID"""
        return self._bookings.get(booking_id)

    def find_all(self) -> List[Booking]:
        """Get all bookings"""
        return list(self._bookings.values())

    def find_by_passenger(self, passenger_name: str) -> List[Booking]:
        """Find all bookings for a specific passenger"""
        return [booking for booking in self._bookings.values()
                if booking.passenger_name.lower() == passenger_name.lower()]

    def find_active_by_passenger(self, passenger_name: str) -> List[Booking]:
        """Find all active bookings for a specific passenger"""
        return [booking for booking in self._bookings.values()
                if booking.passenger_name.lower() == passenger_name.lower()
                and booking.status == BOOKING_STATUS_CONFIRMED]

    def update(self, booking: Booking) -> Booking:
        """Update an existing booking"""
        if booking.booking_id not in self._bookings:
            raise BookingNotFoundError(f"Booking with ID {booking.booking_id} not found")
        self._bookings[booking.booking_id] = booking
        return booking

    def delete(self, booking_id: str) -> None:
        """Delete a booking from the repository"""
        if booking_id not in self._bookings:
            raise BookingNotFoundError(f"Booking with ID {booking_id} not found")
        del self._bookings[booking_id]

    def exists_by_id(self, booking_id: str) -> bool:
        """Check if a booking exists by its ID"""
        return booking_id in self._bookings

    def count(self) -> int:
        """Get the total number of bookings"""
        return len(self._bookings)

    def count_active_bookings(self) -> int:
        """Count all active (confirmed) bookings"""
        return len([b for b in self._bookings.values() if b.status == BOOKING_STATUS_CONFIRMED])

    def count_cancelled_bookings(self) -> int:
        """Count all cancelled bookings"""
        return len([b for b in self._bookings.values() if b.status == BOOKING_STATUS_CANCELLED])