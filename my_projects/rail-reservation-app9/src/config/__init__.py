# src/config/__init__.py

from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass
class Config:
    trains: Dict[str, 'Train'] = None
    passengers: Dict[str, 'Passenger'] = None
    bookings: Dict[str, 'Booking'] = None
    next_booking_id: int = 1000

config = Config(
    trains={},
    passengers={},
    bookings={},
    next_booking_id=1000
)