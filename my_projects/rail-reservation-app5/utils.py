```python
import re
from typing import Optional, Tuple

def validate_passenger_name(name: str) -> bool:
    """Validate passenger name contains only letters and spaces."""
    return bool(re.fullmatch(r'^[A-Za-z\s]+$', name.strip()))

def validate_seat_number(seat: str) -> Tuple[bool, Optional[int]]:
    """Validate seat number is a positive integer."""
    try:
        seat_num = int(seat)
        return seat_num > 0, seat_num
    except ValueError:
        return False, None

def format_seat_list(seats: set) -> str:
    """Format a set of seat numbers into a readable string."""
    if not seats:
        return "No seats available"
    sorted_seats = sorted(seats)
    return ", ".join(map(str, sorted_seats))

def format_booked_seats(bookings: dict) -> str:
    """Format booked seats dictionary into a readable string."""
    if not bookings:
        return "No seats booked"
    return "\n".join(f"Seat {seat}: {name}" for seat, name in sorted(bookings.items()))
```