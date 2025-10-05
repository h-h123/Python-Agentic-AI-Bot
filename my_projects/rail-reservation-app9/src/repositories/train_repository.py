from typing import Dict, Optional, List, Set
from src.config import config
from src.models import Train

class TrainRepository:
    @staticmethod
    def add_train(train_id: str, name: str, total_seats: int) -> bool:
        """Add a new train to the repository."""
        if train_id in config.trains:
            return False

        if total_seats <= 0:
            return False

        config.trains[train_id] = Train(
            train_id=train_id,
            name=name,
            total_seats=total_seats
        )
        return True

    @staticmethod
    def get_train(train_id: str) -> Optional[Train]:
        """Get a train by its ID."""
        return config.trains.get(train_id)

    @staticmethod
    def get_all_trains() -> Dict[str, Train]:
        """Get all trains in the repository."""
        return config.trains

    @staticmethod
    def update_train(train_id: str, name: str = None, total_seats: int = None) -> bool:
        """Update train details."""
        train = config.trains.get(train_id)
        if not train:
            return False

        if name:
            train.name = name
        if total_seats and total_seats > 0:
            # Handle seat updates carefully to avoid data inconsistency
            if total_seats >= len(train.booked_seats):
                train.total_seats = total_seats
            else:
                return False
        return True

    @staticmethod
    def remove_train(train_id: str) -> bool:
        """Remove a train from the repository."""
        if train_id not in config.trains:
            return False

        train = config.trains[train_id]
        if train.booked_seats:
            return False

        del config.trains[train_id]
        return True

    @staticmethod
    def get_available_seats(train_id: str) -> Set[int]:
        """Get all available seats for a train."""
        train = config.trains.get(train_id)
        if not train:
            return set()

        all_seats = set(range(1, train.total_seats + 1))
        return all_seats - train.booked_seats

    @staticmethod
    def get_booked_seats(train_id: str) -> Set[int]:
        """Get all booked seats for a train."""
        train = config.trains.get(train_id)
        if not train:
            return set()
        return train.booked_seats.copy()

    @staticmethod
    def get_train_occupancy(train_id: str) -> float:
        """Get the occupancy percentage of a train."""
        train = config.trains.get(train_id)
        if not train or train.total_seats == 0:
            return 0.0
        return (len(train.booked_seats) / train.total_seats) * 100

    @staticmethod
    def train_exists(train_id: str) -> bool:
        """Check if a train exists in the repository."""
        return train_id in config.trains

    @staticmethod
    def is_seat_available(train_id: str, seat_number: int) -> bool:
        """Check if a specific seat is available on a train."""
        train = config.trains.get(train_id)
        if not train:
            return False
        return train.is_seat_available(seat_number)