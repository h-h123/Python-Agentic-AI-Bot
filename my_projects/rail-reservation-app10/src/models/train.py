from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from src.config.constants import (
    SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED, SEAT_STATUS_MAINTENANCE,
    SEAT_TYPES, DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT,
    DEFAULT_TRAIN_CAPACITY, MIN_SEAT_NUMBER, MAX_SEAT_NUMBER
)

@dataclass
class Train:
    train_id: str
    name: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
    seats: Dict[int, Seat] = field(default_factory=dict)
    capacity: int = DEFAULT_TRAIN_CAPACITY
    train_type: str = "Standard"

    def __post_init__(self):
        if not self.train_id or not isinstance(self.train_id, str):
            raise ValueError("Train ID must be a non-empty string")

        if not self.validate_time_format(self.departure_time) or not self.validate_time_format(self.arrival_time):
            raise ValueError("Invalid time format. Expected HH:MM")

    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        try:
            datetime.strptime(time_str, TIME_FORMAT)
            return True
        except ValueError:
            return False

    def add_seat(self, seat: 'Seat') -> None:
        if not isinstance(seat, Seat):
            raise TypeError("Only Seat objects can be added")

        if seat.seat_number in self.seats:
            raise ValueError(f"Seat {seat.seat_number} already exists in this train")

        if len(self.seats) >= self.capacity:
            raise ValueError(f"Train has reached maximum capacity of {self.capacity} seats")

        if seat.seat_number < MIN_SEAT_NUMBER or seat.seat_number > MAX_SEAT_NUMBER:
            raise ValueError(f"Seat number must be between {MIN_SEAT_NUMBER} and {MAX_SEAT_NUMBER}")

        self.seats[seat.seat_number] = seat

    def remove_seat(self, seat_number: int) -> None:
        if seat_number not in self.seats:
            raise ValueError(f"Seat {seat_number} does not exist in this train")
        del self.seats[seat_number]

    def get_seat(self, seat_number: int) -> Optional['Seat']:
        return self.seats.get(seat_number)

    def get_available_seats(self) -> List['Seat']:
        return [seat for seat in self.seats.values() if seat.status == SEAT_STATUS_AVAILABLE]

    def get_booked_seats(self) -> List['Seat']:
        return [seat for seat in self.seats.values() if seat.status == SEAT_STATUS_BOOKED]

    def get_maintenance_seats(self) -> List['Seat']:
        return [seat for seat in self.seats.values() if seat.status == SEAT_STATUS_MAINTENANCE]

    def get_seat_status(self, seat_number: int) -> Optional[str]:
        seat = self.get_seat(seat_number)
        return seat.status if seat else None

    def update_seat_status(self, seat_number: int, new_status: str) -> None:
        if new_status not in [SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED, SEAT_STATUS_MAINTENANCE]:
            raise ValueError(f"Invalid seat status: {new_status}")

        seat = self.get_seat(seat_number)
        if not seat:
            raise ValueError(f"Seat {seat_number} does not exist")

        seat.status = new_status
        if new_status == SEAT_STATUS_MAINTENANCE:
            seat.last_maintenance_date = datetime.now().strftime(DATE_FORMAT)

    def get_occupancy_rate(self) -> float:
        if not self.seats:
            return 0.0
        booked_seats = len(self.get_booked_seats())
        return (booked_seats / len(self.seats)) * 100

    def __str__(self) -> str:
        return (f"Train {self.train_id}: {self.name} ({self.source} to {self.destination}, "
                f"{self.departure_time}-{self.arrival_time}), "
                f"Capacity: {len(self.seats)}/{self.capacity} seats")