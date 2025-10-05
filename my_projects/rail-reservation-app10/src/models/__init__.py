from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from uuid import uuid4
from src.config.constants import (
    SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED, SEAT_STATUS_MAINTENANCE,
    BOOKING_STATUS_CONFIRMED, BOOKING_STATUS_CANCELLED,
    SEAT_TYPES, DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT
)

@dataclass
class Seat:
    seat_number: int
    status: str = SEAT_STATUS_AVAILABLE
    seat_type: str = SEAT_TYPES["STANDARD"]
    last_maintenance_date: Optional[str] = None

    def __post_init__(self):
        if self.seat_number < 1 or self.seat_number > 50:
            raise ValueError("Seat number must be between 1 and 50")

    def book(self):
        if self.status != SEAT_STATUS_AVAILABLE:
            raise ValueError("Seat is not available for booking")
        self.status = SEAT_STATUS_BOOKED

    def release(self):
        if self.status != SEAT_STATUS_BOOKED:
            raise ValueError("Seat is not booked")
        self.status = SEAT_STATUS_AVAILABLE

    def mark_maintenance(self):
        self.status = SEAT_STATUS_MAINTENANCE
        self.last_maintenance_date = datetime.now().strftime(DATE_FORMAT)

@dataclass
class Train:
    train_id: str
    name: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
    seats: Dict[int, Seat] = field(default_factory=dict)
    capacity: int = 50

    def add_seat(self, seat: Seat):
        if seat.seat_number in self.seats:
            raise ValueError(f"Seat {seat.seat_number} already exists")
        if len(self.seats) >= self.capacity:
            raise ValueError("Train has reached maximum capacity")
        self.seats[seat.seat_number] = seat

    def get_seat(self, seat_number: int) -> Optional[Seat]:
        return self.seats.get(seat_number)

    def get_available_seats(self) -> List[Seat]:
        return [seat for seat in self.seats.values() if seat.status == SEAT_STATUS_AVAILABLE]

@dataclass
class Booking:
    booking_id: str = field(default_factory=lambda: f"BK-{str(uuid4())[:8].upper()}")
    train_id: str = ""
    seat_number: int = 0
    passenger_name: str = ""
    booking_time: str = field(default_factory=lambda: datetime.now().strftime(DATETIME_FORMAT))
    status: str = BOOKING_STATUS_CONFIRMED
    price: float = 0.0

    def cancel(self):
        if self.status != BOOKING_STATUS_CONFIRMED:
            raise ValueError("Booking is not active")
        self.status = BOOKING_STATUS_CANCELLED

__all__ = ["Train", "Seat", "Booking"]