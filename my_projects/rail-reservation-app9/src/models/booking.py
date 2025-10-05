from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Booking:
    booking_id: str
    passenger_id: str
    train_id: str
    seat_number: int
    booking_time: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def cancel(self) -> None:
        """Mark the booking as inactive (cancelled)."""
        self.is_active = False

    def is_valid(self) -> bool:
        """Check if the booking is still active."""
        return self.is_active

    def get_booking_details(self) -> dict:
        """Return booking details as a dictionary."""
        return {
            "booking_id": self.booking_id,
            "passenger_id": self.passenger_id,
            "train_id": self.train_id,
            "seat_number": self.seat_number,
            "booking_time": self.booking_time.isoformat(),
            "is_active": self.is_active
        }

    @classmethod
    def create_booking(cls, passenger_id: str, train_id: str, seat_number: int, booking_id: str) -> 'Booking':
        """Factory method to create a new booking."""
        return cls(
            booking_id=booking_id,
            passenger_id=passenger_id,
            train_id=train_id,
            seat_number=seat_number
        )