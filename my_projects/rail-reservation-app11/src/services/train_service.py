from typing import List, Dict, Optional
from datetime import datetime
import uuid
from src.models.train import Train, Seat
from src.config.settings import settings

class TrainService:
    def __init__(self):
        self.trains: Dict[str, Train] = {}

    def add_train(self, train: Train) -> None:
        """Add a new train to the service"""
        if train.train_id in self.trains:
            raise ValueError(f"Train with ID {train.train_id} already exists")
        self.trains[train.train_id] = train

    def get_train(self, train_id: str) -> Optional[Train]:
        """Get a train by its ID"""
        return self.trains.get(train_id)

    def get_all_trains(self) -> List[Train]:
        """Get all available trains"""
        return list(self.trains.values())

    def update_train(self, train_id: str, **kwargs) -> Train:
        """Update train information"""
        train = self.get_train(train_id)
        if not train:
            raise ValueError(f"Train with ID {train_id} not found")

        for key, value in kwargs.items():
            if hasattr(train, key):
                setattr(train, key, value)

        return train

    def remove_train(self, train_id: str) -> None:
        """Remove a train from the service"""
        if train_id not in self.trains:
            raise ValueError(f"Train with ID {train_id} not found")
        del self.trains[train_id]

    def get_available_seats(self, train_id: str, seat_class: Optional[str] = None) -> List[Seat]:
        """Get available seats for a train, optionally filtered by class"""
        train = self.get_train(train_id)
        if not train:
            raise ValueError(f"Train with ID {train_id} not found")

        if seat_class:
            return train.get_available_seats_by_class(seat_class)
        return [seat for seat in train.seats if not seat.is_booked]

    def get_train_seat_map(self, train_id: str) -> Dict[str, List[Dict]]:
        """Get seat map for a train organized by class"""
        train = self.get_train(train_id)
        if not train:
            raise ValueError(f"Train with ID {train_id} not found")

        seat_map = {}
        for seat_class in train.seat_classes:
            seat_map[seat_class] = [
                {
                    "seat_number": seat.seat_number,
                    "is_booked": seat.is_booked,
                    "price": seat.price
                }
                for seat in train.seats
                if seat.seat_class.lower() == seat_class.lower()
            ]
        return seat_map

    def get_train_occupancy(self, train_id: str) -> float:
        """Get occupancy percentage for a train"""
        train = self.get_train(train_id)
        if not train:
            raise ValueError(f"Train with ID {train_id} not found")

        booked_seats = sum(1 for seat in train.seats if seat.is_booked)
        return (booked_seats / train.total_seats) * 100

    def search_trains(self, source: Optional[str] = None,
                     destination: Optional[str] = None,
                     date: Optional[datetime] = None) -> List[Train]:
        """Search trains based on criteria"""
        results = self.get_all_trains()

        if source:
            results = [t for t in results if t.source.lower() == source.lower()]
        if destination:
            results = [t for t in results if t.destination.lower() == destination.lower()]
        if date:
            results = [t for t in results if t.departure_time.date() == date.date()]

        return results