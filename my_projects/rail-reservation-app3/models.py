Here's a `models.py` implementation that defines the core data models for your railway reservation system:

```python
from dataclasses import dataclass
from typing import Optional, Set, Dict
from enum import Enum, auto

class SeatStatus(Enum):
    """Enumeration for seat status"""
    AVAILABLE = auto()
    BOOKED = auto()
    MAINTENANCE = auto()

@dataclass
class Passenger:
    """Data class representing a passenger"""
    name: str
    contact: Optional[str] = None
    email: Optional[str] = None

@dataclass
class Seat:
    """Data class representing a train seat"""
    number: int
    status: SeatStatus = SeatStatus.AVAILABLE
    passenger: Optional[Passenger] = None
    booking_reference: Optional[str] = None

@dataclass
class Booking:
    """Data class representing a booking"""
    reference: str
    seat: Seat
    passenger: Passenger
    booking_time: str  # Could be datetime in real implementation
    is_cancelled: bool = False

class Train:
    """Class representing a train with seats and bookings"""

    def __init__(self, train_number: str, total_seats: int = 100):
        self.train_number = train_number
        self.seats: Dict[int, Seat] = {
            num: Seat(num) for num in range(1, total_seats + 1)
        }
        self.bookings: Dict[str, Booking] = {}

    def get_available_seats(self) -> Set[int]:
        """Get set of available seat numbers"""
        return {
            seat.number for seat in self.seats.values()
            if seat.status == SeatStatus.AVAILABLE
        }

    def get_booked_seats(self) -> Dict[int, str]:
        """Get dictionary of booked seat numbers and passenger names"""
        return {
            seat.number: seat.passenger.name
            for seat in self.seats.values()
            if seat.status == SeatStatus.BOOKED
        }

    def get_seat(self, seat_number: int) -> Optional[Seat]:
        """Get seat by number if it exists"""
        return self.seats.get(seat_number)
```

This implementation:

1. Uses Python's dataclasses for clean data representation
2. Includes proper type hints
3. Defines core models:
   - `SeatStatus` enum for seat states
   - `Passenger` for passenger information
   - `Seat` for individual seats
   - `Booking` for booking records
   - `Train` as the main container class
4. Provides basic query methods
5. Follows object-oriented principles
6. Maintains consistency with the existing system's functionality

The models can be used by your other components (booking.py, cancellation.py) while keeping the data structure separate from business logic.