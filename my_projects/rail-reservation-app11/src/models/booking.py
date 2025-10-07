from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid
from src.models.train import Train, Seat
from src.models.passenger import Passenger

@dataclass
class Booking:
    booking_id: str
    train: Train
    passenger: Passenger
    seat: Seat
    booking_time: datetime = field(default_factory=datetime.now)
    status: str = "confirmed"
    cancellation_fee: Optional[float] = None

    def __post_init__(self):
        if isinstance(self.booking_id, str) and not self.booking_id:
            self.booking_id = str(uuid.uuid4())

        if not hasattr(self.passenger, 'passenger_id') or not self.passenger.passenger_id:
            self.passenger.passenger_id = str(uuid.uuid4())

        self.passenger.add_booking(self.booking_id)

    def cancel(self):
        self.status = "cancelled"
        self.seat.is_booked = False
        self.train.available_seats += 1
        self.passenger.remove_booking(self.booking_id)

        if self.cancellation_fee is None:
            from src.config.settings import settings
            self.cancellation_fee = self.seat.price * (float(settings.cancellation_fee_percentage) / 100)

    def get_booking_details(self) -> dict:
        return {
            "booking_id": self.booking_id,
            "train_id": self.train.train_id,
            "passenger_name": self.passenger.name,
            "seat_number": self.seat.seat_number,
            "seat_class": self.seat.seat_class,
            "booking_time": self.booking_time.isoformat(),
            "status": self.status,
            "price": self.seat.price,
            "cancellation_fee": self.cancellation_fee
        }