from typing import Dict, Set, Optional, List
from dataclasses import dataclass
from booking_repository import BookingRepository, InMemoryBookingRepository
from train_repository import Train, TrainRepository, InMemoryTrainRepository

@dataclass
class TrainWithBookings:
    train: Train
    booking_repository: BookingRepository

    def get_available_seats(self) -> Set[int]:
        return self.booking_repository.get_available_seats()

    def get_booked_seats(self) -> Dict[int, str]:
        return self.booking_repository.get_all_bookings()

    def book_seat(self, passenger_name: str) -> Optional[int]:
        available_seats = self.get_available_seats()
        if not available_seats:
            return None

        seat_number = min(available_seats)
        if self.booking_repository.save_booking(seat_number, passenger_name):
            return seat_number
        return None

    def cancel_booking(self, seat_number: int) -> Optional[str]:
        return self.booking_repository.remove_booking(seat_number)

class TrainService:
    def __init__(self):
        self.train_repository: TrainRepository = InMemoryTrainRepository()
        self._train_bookings: Dict[str, TrainWithBookings] = {}

    def add_train(self, train: Train) -> bool:
        if self.train_repository.add_train(train):
            self._train_bookings[train.train_id] = TrainWithBookings(
                train=train,
                booking_repository=InMemoryBookingRepository(train.total_seats)
            )
            return True
        return False

    def get_train(self, train_id: str) -> Optional[Train]:
        return self.train_repository.get_train(train_id)

    def get_train_with_bookings(self, train_id: str) -> Optional[TrainWithBookings]:
        return self._train_bookings.get(train_id)

    def get_all_trains(self) -> List[Train]:
        return self.train_repository.get_all_trains()

    def book_seat(self, train_id: str, passenger_name: str) -> Optional[int]:
        train_bookings = self.get_train_with_bookings(train_id)
        if not train_bookings:
            return None
        return train_bookings.book_seat(passenger_name)

    def cancel_booking(self, train_id: str, seat_number: int) -> Optional[str]:
        train_bookings = self.get_train_with_bookings(train_id)
        if not train_bookings:
            return None
        return train_bookings.cancel_booking(seat_number)

    def get_available_seats(self, train_id: str) -> Set[int]:
        train_bookings = self.get_train_with_bookings(train_id)
        if not train_bookings:
            return set()
        return train_bookings.get_available_seats()

    def get_booked_seats(self, train_id: str) -> Dict[int, str]:
        train_bookings = self.get_train_with_bookings(train_id)
        if not train_bookings:
            return {}
        return train_bookings.get_booked_seats()