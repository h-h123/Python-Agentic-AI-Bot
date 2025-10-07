from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid

@dataclass
class Seat:
    seat_number: str
    seat_class: str
    is_booked: bool = False
    price: float = 0.0

    def __post_init__(self):
        if self.price == 0.0:
            from src.config.settings import settings
            if self.seat_class.lower() == "economy":
                self.price = float(settings.price_economy)
            elif self.seat_class.lower() == "business":
                self.price = float(settings.price_business)

@dataclass
class Train:
    train_id: str
    name: str
    source: str
    destination: str
    departure_time: datetime
    total_seats: int
    available_seats: int = None
    seats: List[Seat] = field(default_factory=list)
    seat_classes: List[str] = field(default_factory=list)

    def __post_init__(self):
        from src.config.settings import settings
        if self.available_seats is None:
            self.available_seats = self.total_seats

        if not self.seats:
            economy_seats = int(self.total_seats * 0.8)
            business_seats = self.total_seats - economy_seats

            self.seats = (
                [Seat(f"{i+1}", "Economy") for i in range(economy_seats)] +
                [Seat(f"{i+1+economy_seats}", "Business") for i in range(business_seats)]
            )

        if not self.seat_classes:
            self.seat_classes = settings.default_seat_classes

    def get_available_seats_by_class(self, seat_class: str) -> List[Seat]:
        return [seat for seat in self.seats
                if not seat.is_booked and seat.seat_class.lower() == seat_class.lower()]