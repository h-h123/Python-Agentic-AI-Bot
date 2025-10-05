from typing import Dict, List, Optional
from src.models import Train, Seat
from src.exceptions import SeatNotAvailableError
from src.config.constants import (
    SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED,
    SEAT_STATUS_MAINTENANCE, DEFAULT_TRAIN_CAPACITY,
    ERROR_MESSAGES
)

class TrainService:
    def __init__(self):
        self.trains: Dict[str, Train] = {}

    def add_train(self, train: Train) -> None:
        if train.train_id in self.trains:
            raise ValueError(f"Train with ID {train.train_id} already exists")
        self.trains[train.train_id] = train

    def get_train(self, train_id: str) -> Optional[Train]:
        return self.trains.get(train_id)

    def get_all_trains(self) -> List[Train]:
        return list(self.trains.values())

    def add_seat(self, train_id: str, seat: Seat) -> None:
        train = self.get_train(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])
        train.add_seat(seat)

    def get_seat(self, train_id: str, seat_number: int) -> Optional[Seat]:
        train = self.get_train(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])
        return train.get_seat(seat_number)

    def get_available_seats(self, train_id: str) -> List[Seat]:
        train = self.get_train(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])
        return train.get_available_seats()

    def get_booked_seats(self, train_id: str) -> List[Seat]:
        train = self.get_train(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])
        return train.get_booked_seats()

    def update_seat_status(self, train_id: str, seat_number: int, status: str) -> None:
        train = self.get_train(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])

        seat = train.get_seat(seat_number)
        if not seat:
            raise ValueError(ERROR_MESSAGES["invalid_seat"])

        if status not in [SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED, SEAT_STATUS_MAINTENANCE]:
            raise ValueError(f"Invalid seat status: {status}")

        seat.status = status
        if status == SEAT_STATUS_MAINTENANCE:
            seat.mark_maintenance()

    def remove_train(self, train_id: str) -> None:
        if train_id not in self.trains:
            raise ValueError(f"Train with ID {train_id} not found")
        del self.trains[train_id]

    def get_train_occupancy(self, train_id: str) -> float:
        train = self.get_train(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])
        return train.get_occupancy_rate()

    def get_seat_status(self, train_id: str, seat_number: int) -> Optional[str]:
        train = self.get_train(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])
        return train.get_seat_status(seat_number)

    def initialize_train_seats(self, train_id: str, seat_type: str = "Standard") -> None:
        train = self.get_train(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])

        if len(train.seats) > 0:
            raise ValueError("Train already has seats initialized")

        for seat_num in range(1, DEFAULT_TRAIN_CAPACITY + 1):
            seat = Seat(seat_number=seat_num, seat_type=seat_type)
            train.add_seat(seat)