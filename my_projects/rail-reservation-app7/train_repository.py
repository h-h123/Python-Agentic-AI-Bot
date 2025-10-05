from typing import Dict, Set, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Train:
    train_id: str
    name: str
    total_seats: int
    source: str
    destination: str
    departure_time: str

class TrainRepository(ABC):
    @abstractmethod
    def add_train(self, train: Train) -> bool:
        pass

    @abstractmethod
    def get_train(self, train_id: str) -> Optional[Train]:
        pass

    @abstractmethod
    def get_all_trains(self) -> List[Train]:
        pass

    @abstractmethod
    def update_train(self, train_id: str, **kwargs) -> bool:
        pass

    @abstractmethod
    def delete_train(self, train_id: str) -> bool:
        pass

class InMemoryTrainRepository(TrainRepository):
    def __init__(self):
        self.trains: Dict[str, Train] = {}

    def add_train(self, train: Train) -> bool:
        if train.train_id in self.trains:
            return False
        self.trains[train.train_id] = train
        return True

    def get_train(self, train_id: str) -> Optional[Train]:
        return self.trains.get(train_id)

    def get_all_trains(self) -> List[Train]:
        return list(self.trains.values())

    def update_train(self, train_id: str, **kwargs) -> bool:
        if train_id not in self.trains:
            return False

        train = self.trains[train_id]
        for key, value in kwargs.items():
            if hasattr(train, key):
                setattr(train, key, value)
        return True

    def delete_train(self, train_id: str) -> bool:
        if train_id in self.trains:
            del self.trains[train_id]
            return True
        return False