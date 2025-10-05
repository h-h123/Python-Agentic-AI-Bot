from typing import Dict, Set, Optional
from abc import ABC, abstractmethod

class BookingRepository(ABC):
    @abstractmethod
    def save_booking(self, seat_number: int, passenger_name: str) -> bool:
        pass

    @abstractmethod
    def remove_booking(self, seat_number: int) -> Optional[str]:
        pass

    @abstractmethod
    def get_all_bookings(self) -> Dict[int, str]:
        pass

    @abstractmethod
    def get_available_seats(self) -> Set[int]:
        pass

    @abstractmethod
    def is_seat_available(self, seat_number: int) -> bool:
        pass

class InMemoryBookingRepository(BookingRepository):
    def __init__(self, total_seats: int = 100):
        self.total_seats = total_seats
        self.available_seats = set(range(1, total_seats + 1))
        self.booked_seats: Dict[int, str] = {}

    def save_booking(self, seat_number: int, passenger_name: str) -> bool:
        if seat_number in self.available_seats:
            self.available_seats.remove(seat_number)
            self.booked_seats[seat_number] = passenger_name
            return True
        return False

    def remove_booking(self, seat_number: int) -> Optional[str]:
        if seat_number in self.booked_seats:
            passenger_name = self.booked_seats.pop(seat_number)
            self.available_seats.add(seat_number)
            return passenger_name
        return None

    def get_all_bookings(self) -> Dict[int, str]:
        return self.booked_seats.copy()

    def get_available_seats(self) -> Set[int]:
        return self.available_seats.copy()

    def is_seat_available(self, seat_number: int) -> bool:
        return seat_number in self.available_seats