from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class Seat:
    number: int
    is_available: bool = True

@dataclass
class Booking:
    booking_id: int
    seat_number: int
    passenger_name: str
    booking_time: datetime = datetime.now()

class SeatManager:
    def __init__(self, total_seats: int = 100):
        self.seats: Dict[int, Seat] = {
            number: Seat(number) for number in range(1, total_seats + 1)
        }

    def get_available_seats(self) -> List[int]:
        return [
            seat.number for seat in self.seats.values()
            if seat.is_available
        ]

    def book_seat(self, seat_number: int) -> bool:
        if seat_number in self.seats and self.seats[seat_number].is_available:
            self.seats[seat_number].is_available = False
            return True
        return False

    def release_seat(self, seat_number: int) -> bool:
        if seat_number in self.seats and not self.seats[seat_number].is_available:
            self.seats[seat_number].is_available = True
            return True
        return False

class BookingRecord:
    def __init__(self):
        self.bookings: Dict[int, Booking] = {}
        self.next_booking_id = 1

    def add_booking(self, seat_number: int, passenger_name: str) -> int:
        booking_id = self.next_booking_id
        self.bookings[booking_id] = Booking(
            booking_id=booking_id,
            seat_number=seat_number,
            passenger_name=passenger_name
        )
        self.next_booking_id += 1
        return booking_id

    def cancel_booking(self, booking_id: int) -> Optional[Booking]:
        return self.bookings.pop(booking_id, None)

    def get_booking_by_seat(self, seat_number: int) -> Optional[Booking]:
        for booking in self.bookings.values():
            if booking.seat_number == seat_number:
                return booking
        return None