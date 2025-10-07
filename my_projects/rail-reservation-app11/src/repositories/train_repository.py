from typing import Dict, List, Optional
from src.models.train import Train
from src.models.booking import Booking
from src.models.payment import Payment
from src.config.settings import settings

class TrainRepository:
    def __init__(self):
        self.trains: Dict[str, Train] = {}

    def save(self, train: Train) -> Train:
        """Save a train to the repository"""
        self.trains[train.train_id] = train
        return train

    def find_by_id(self, train_id: str) -> Optional[Train]:
        """Find a train by its ID"""
        return self.trains.get(train_id)

    def find_all(self) -> List[Train]:
        """Get all trains from the repository"""
        return list(self.trains.values())

    def update(self, train: Train) -> Train:
        """Update a train in the repository"""
        if train.train_id not in self.trains:
            raise ValueError(f"Train with ID {train.train_id} not found")
        self.trains[train.train_id] = train
        return train

    def delete(self, train_id: str) -> None:
        """Delete a train from the repository"""
        if train_id not in self.trains:
            raise ValueError(f"Train with ID {train_id} not found")
        del self.trains[train_id]

    def find_by_route(self, source: str, destination: str) -> List[Train]:
        """Find trains by route (source and destination)"""
        return [
            train for train in self.trains.values()
            if train.source.lower() == source.lower()
            and train.destination.lower() == destination.lower()
        ]

    def find_by_departure_date(self, date: str) -> List[Train]:
        """Find trains by departure date"""
        return [
            train for train in self.trains.values()
            if train.departure_time.date().isoformat() == date
        ]