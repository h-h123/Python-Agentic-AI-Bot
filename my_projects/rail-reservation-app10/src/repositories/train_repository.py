# src/repositories/train_repository.py

from typing import Dict, List, Optional
from src.models import Train
from src.exceptions import SeatNotAvailableError
from src.config.constants import (
    SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED,
    SEAT_STATUS_MAINTENANCE, DEFAULT_TRAIN_CAPACITY,
    ERROR_MESSAGES
)

class TrainRepository:
    def __init__(self):
        self._trains: Dict[str, Train] = {}

    def save(self, train: Train) -> Train:
        """Save a train to the repository"""
        if train.train_id in self._trains:
            raise ValueError(f"Train with ID {train.train_id} already exists")
        self._trains[train.train_id] = train
        return train

    def find_by_id(self, train_id: str) -> Optional[Train]:
        """Find a train by its ID"""
        return self._trains.get(train_id)

    def find_all(self) -> List[Train]:
        """Get all trains"""
        return list(self._trains.values())

    def delete(self, train_id: str) -> None:
        """Delete a train from the repository"""
        if train_id not in self._trains:
            raise ValueError(f"Train with ID {train_id} not found")
        del self._trains[train_id]

    def exists_by_id(self, train_id: str) -> bool:
        """Check if a train exists by its ID"""
        return train_id in self._trains

    def count(self) -> int:
        """Get the total number of trains"""
        return len(self._trains)

    def update(self, train: Train) -> Train:
        """Update an existing train"""
        if train.train_id not in self._trains:
            raise ValueError(f"Train with ID {train.train_id} not found")
        self._trains[train.train_id] = train
        return train

    def find_by_route(self, source: str, destination: str) -> List[Train]:
        """Find trains by source and destination"""
        return [train for train in self._trains.values()
                if train.source.lower() == source.lower()
                and train.destination.lower() == destination.lower()]

    def find_by_name(self, name: str) -> List[Train]:
        """Find trains by name (partial match)"""
        return [train for train in self._trains.values()
                if name.lower() in train.name.lower()]

    def get_train_occupancy(self, train_id: str) -> float:
        """Get the occupancy rate of a specific train"""
        train = self.find_by_id(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])

        total_seats = len(train.seats)
        if total_seats == 0:
            return 0.0

        booked_seats = len([seat for seat in train.seats.values() if seat.status == SEAT_STATUS_BOOKED])
        return (booked_seats / total_seats) * 100