Here's a useful `utils.py` implementation that complements your railway reservation system with utility functions:

```python
import random
import string
from typing import Optional, List, Dict, Any
from datetime import datetime

def generate_booking_reference(length: int = 8) -> str:
    """Generate a random alphanumeric booking reference"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def validate_seat_number(seat_number: int, total_seats: int) -> bool:
    """Validate that a seat number is within the valid range"""
    return 1 <= seat_number <= total_seats

def format_booking_info(seat_number: int, passenger_name: str, booking_time: Optional[datetime] = None) -> str:
    """Format booking information for display"""
    time_str = booking_time.strftime("%Y-%m-%d %H:%M:%S") if booking_time else "N/A"
    return f"Seat {seat_number}: {passenger_name} (Booked at: {time_str})"

def parse_seat_range(seat_range: str) -> List[int]:
    """
    Parse seat range string (e.g., '1-5,7,10-12') into list of seat numbers
    Returns empty list for invalid input
    """
    try:
        seats = []
        for part in seat_range.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                seats.extend(range(start, end + 1))
            else:
                seats.append(int(part))
        return list(set(seats))  # Remove duplicates
    except ValueError:
        return []

def get_current_timestamp() -> str:
    """Get current timestamp as formatted string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate_cancellation_fee(booked_time: datetime, cancellation_time: datetime) -> float:
    """
    Calculate cancellation fee based on time difference
    Example implementation - adjust as needed
    """
    time_diff = (cancellation_time - booked_time).total_seconds() / 3600  # hours
    if time_diff < 24:
        return 20.0  # High fee for last-minute cancellation
    elif time_diff < 72:
        return 10.0  # Medium fee
    return 5.0  # Low fee

def export_bookings_to_dict(bookings: Dict[int, Any]) -> Dict[str, Any]:
    """Convert bookings dictionary to export-friendly format"""
    return {
        "timestamp": get_current_timestamp(),
        "total_bookings": len(bookings),
        "bookings": [
            {
                "seat_number": seat,
                "passenger_name": name,
                "status": "booked"
            }
            for seat, name in bookings.items()
        ]
    }
```

This `utils.py` provides:

1. **Booking reference generation** - For creating unique booking IDs
2. **Input validation** - For seat numbers and ranges
3. **Data formatting** - For consistent display of booking information
4. **Time utilities** - For timestamps and cancellation fee calculations
5. **Data parsing** - For seat range inputs
6. **Export functionality** - For converting bookings to a standard format

The functions are designed to be:
- Reusable across different parts of the system
- Type-hinted for better code clarity
- Documented with docstrings
- Complementary to the existing system components

You can import and use these utilities in your main application, booking manager, or cancellation service as needed.