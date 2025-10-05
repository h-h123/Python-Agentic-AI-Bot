from dataclasses import dataclass, field
from typing import Set

@dataclass
class Train:
    train_id: str
    name: str
    total_seats: int
    booked_seats: Set[int] = field(default_factory=set)

    def is_seat_available(self, seat_number: int) -> bool:
        """Check if a seat is available for booking."""
        return 1 <= seat_number <= self.total_seats and seat_number not in self.booked_seats

    def book_seat(self, seat_number: int) -> bool:
        """Book a seat if it's available."""
        if self.is_seat_available(seat_number):
            self.booked_seats.add(seat_number)
            return True
        return False

    def cancel_seat(self, seat_number: int) -> bool:
        """Cancel a booked seat."""
        if seat_number in self.booked_seats:
            self.booked_seats.remove(seat_number)
            return True
        return False

    def get_available_seats_count(self) -> int:
        """Get the number of available seats."""
        return self.total_seats - len(self.booked_seats)

    def get_booked_seats(self) -> Set[int]:
        """Get all booked seat numbers."""
        return self.booked_seats.copy()