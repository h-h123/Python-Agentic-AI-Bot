from dataclasses import dataclass
from typing import Optional

@dataclass
class Seat:
    number: int
    is_booked: bool = False
    passenger_name: Optional[str] = None
    coach: Optional[str] = None
    seat_type: str = "standard"

    def book(self, passenger_name: str, coach: Optional[str] = None) -> bool:
        if not self.is_booked:
            self.is_booked = True
            self.passenger_name = passenger_name
            self.coach = coach
            return True
        return False

    def cancel(self) -> bool:
        if self.is_booked:
            self.is_booked = False
            self.passenger_name = None
            return True
        return False

    def __str__(self) -> str:
        status = "Booked" if self.is_booked else "Available"
        coach_info = f" ({self.coach})" if self.coach else ""
        return f"Seat {self.number}{coach_info}: {status}" + (
            f" - {self.passenger_name}" if self.is_booked else ""
        )

class SeatFactory:
    @staticmethod
    def create_seat(seat_number: int, seat_type: str = "standard") -> Seat:
        return Seat(number=seat_number, seat_type=seat_type)

class SeatManager:
    def __init__(self, total_seats: int = 100):
        self.seats = [SeatFactory.create_seat(i) for i in range(1, total_seats + 1)]

    def get_seat(self, seat_number: int) -> Optional[Seat]:
        if 1 <= seat_number <= len(self.seats):
            return self.seats[seat_number - 1]
        return None

    def get_available_seats(self) -> list[Seat]:
        return [seat for seat in self.seats if not seat.is_booked]

    def get_booked_seats(self) -> list[Seat]:
        return [seat for seat in self.seats if seat.is_booked]