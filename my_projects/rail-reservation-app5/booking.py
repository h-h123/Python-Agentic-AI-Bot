```python
from typing import Optional, Tuple, Dict, Set
from database import DatabaseManager

class RailwayReservationSystem:
    def __init__(self, total_seats: int = 100):
        self.db = DatabaseManager()
        self.db.initialize_seats(total_seats)

    def book_seat(self, passenger_name: str) -> Tuple[Optional[int], str]:
        return self.db.book_seat(passenger_name)

    def cancel_booking(self, seat_number: int) -> Tuple[bool, str]:
        return self.db.cancel_booking(seat_number)

    def display_available_seats(self) -> Set[int]:
        return self.db.get_available_seats()

    def display_booked_seats(self) -> Dict[int, str]:
        return self.db.get_booked_seats()

    def close(self) -> None:
        self.db.close()
```