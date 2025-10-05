from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional
from datetime import datetime
import uuid

@dataclass
class Train:
    train_id: str
    name: str
    total_seats: int
    booked_seats: Set[int] = field(default_factory=set)

    def is_seat_available(self, seat_number: int) -> bool:
        return 1 <= seat_number <= self.total_seats and seat_number not in self.booked_seats

    def book_seat(self, seat_number: int) -> bool:
        if self.is_seat_available(seat_number):
            self.booked_seats.add(seat_number)
            return True
        return False

    def cancel_seat(self, seat_number: int) -> bool:
        if seat_number in self.booked_seats:
            self.booked_seats.remove(seat_number)
            return True
        return False

@dataclass
class Passenger:
    passenger_id: str
    name: str
    booking_ids: List[str] = field(default_factory=list)

    def add_booking(self, booking_id: str) -> None:
        self.booking_ids.append(booking_id)

    def remove_booking(self, booking_id: str) -> bool:
        if booking_id in self.booking_ids:
            self.booking_ids.remove(booking_id)
            return True
        return False

@dataclass
class Booking:
    booking_id: str
    passenger_id: str
    train_id: str
    seat_number: int
    booking_time: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def cancel(self) -> None:
        self.is_active = False