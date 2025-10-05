from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta
from uuid import uuid4
from src.config.constants import (
    BOOKING_STATUS_CONFIRMED,
    BOOKING_STATUS_CANCELLED,
    SEAT_TYPES,
    SEAT_PRICES,
    DATETIME_FORMAT,
    BOOKING_EXPIRY_HOURS,
    ERROR_MESSAGES
)

@dataclass
class Booking:
    booking_id: str = field(default_factory=lambda: f"BK-{str(uuid4())[:8].upper()}")
    train_id: str = ""
    seat_number: int = 0
    passenger_name: str = ""
    booking_time: str = field(default_factory=lambda: datetime.now().strftime(DATETIME_FORMAT))
    status: str = BOOKING_STATUS_CONFIRMED
    price: float = 0.0
    seat_type: str = SEAT_TYPES["STANDARD"]
    expiry_time: str = field(init=False)

    def __post_init__(self):
        self.expiry_time = (datetime.now() + timedelta(hours=BOOKING_EXPIRY_HOURS)).strftime(DATETIME_FORMAT)
        self.price = SEAT_PRICES.get(self.seat_type, SEAT_PRICES[SEAT_TYPES["STANDARD"]])

    def cancel(self) -> None:
        if self.status != BOOKING_STATUS_CONFIRMED:
            raise ValueError(ERROR_MESSAGES["booking_not_found"])
        self.status = BOOKING_STATUS_CANCELLED

    def is_expired(self) -> bool:
        expiry_datetime = datetime.strptime(self.expiry_time, DATETIME_FORMAT)
        return datetime.now() > expiry_datetime

    def update_seat_type(self, new_seat_type: str) -> None:
        if new_seat_type not in SEAT_TYPES.values():
            raise ValueError(f"Invalid seat type: {new_seat_type}")
        self.seat_type = new_seat_type
        self.price = SEAT_PRICES[new_seat_type]

    def __str__(self) -> str:
        return (f"Booking {self.booking_id}: Train {self.train_id}, Seat {self.seat_number} ({self.seat_type}), "
                f"Passenger: {self.passenger_name}, Status: {self.status}, "
                f"Price: ${self.price:.2f}, Booked at: {self.booking_time}")