from dataclasses import dataclass
from typing import Optional

@dataclass
class Passenger:
    passenger_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    bookings: list = None

    def __post_init__(self):
        if self.bookings is None:
            self.bookings = []

    def add_booking(self, booking_id: str):
        if booking_id not in self.bookings:
            self.bookings.append(booking_id)

    def remove_booking(self, booking_id: str):
        if booking_id in self.bookings:
            self.bookings.remove(booking_id)