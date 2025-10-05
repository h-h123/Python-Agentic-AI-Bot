from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Seat:
    seat_number: int
    is_booked: bool = False
    booking_id: Optional[str] = None
    passenger_id: Optional[str] = None

    def book(self, booking_id: str, passenger_id: str) -> bool:
        """Book this seat if it's available."""
        if not self.is_booked:
            self.is_booked = True
            self.booking_id = booking_id
            self.passenger_id = passenger_id
            return True
        return False

    def cancel_booking(self) -> bool:
        """Cancel the booking for this seat."""
        if self.is_booked:
            self.is_booked = False
            self.booking_id = None
            self.passenger_id = None
            return True
        return False

    def get_status(self) -> dict:
        """Return the current status of the seat."""
        return {
            "seat_number": self.seat_number,
            "is_booked": self.is_booked,
            "booking_id": self.booking_id,
            "passenger_id": self.passenger_id
        }

    @classmethod
    def create_seat(cls, seat_number: int) -> 'Seat':
        """Factory method to create a new seat."""
        return cls(seat_number=seat_number)