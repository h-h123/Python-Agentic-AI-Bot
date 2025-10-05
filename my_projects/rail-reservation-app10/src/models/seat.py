from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from src.config.constants import (
    SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED, SEAT_STATUS_MAINTENANCE,
    SEAT_TYPES, DATE_FORMAT, MIN_SEAT_NUMBER, MAX_SEAT_NUMBER
)

@dataclass
class Seat:
    seat_number: int
    status: str = SEAT_STATUS_AVAILABLE
    seat_type: str = SEAT_TYPES["STANDARD"]
    last_maintenance_date: Optional[str] = None
    price: float = 0.0

    def __post_init__(self):
        if self.seat_number < MIN_SEAT_NUMBER or self.seat_number > MAX_SEAT_NUMBER:
            raise ValueError(f"Seat number must be between {MIN_SEAT_NUMBER} and {MAX_SEAT_NUMBER}")

        if self.seat_type not in SEAT_TYPES.values():
            raise ValueError(f"Invalid seat type. Must be one of: {', '.join(SEAT_TYPES.values())}")

    def book(self) -> None:
        if self.status != SEAT_STATUS_AVAILABLE:
            raise ValueError("Seat is not available for booking")
        self.status = SEAT_STATUS_BOOKED

    def release(self) -> None:
        if self.status != SEAT_STATUS_BOOKED:
            raise ValueError("Seat is not booked")
        self.status = SEAT_STATUS_AVAILABLE

    def mark_maintenance(self) -> None:
        self.status = SEAT_STATUS_MAINTENANCE
        self.last_maintenance_date = datetime.now().strftime(DATE_FORMAT)

    def is_available(self) -> bool:
        return self.status == SEAT_STATUS_AVAILABLE

    def is_booked(self) -> bool:
        return self.status == SEAT_STATUS_BOOKED

    def is_in_maintenance(self) -> bool:
        return self.status == SEAT_STATUS_MAINTENANCE

    def __str__(self) -> str:
        return (f"Seat {self.seat_number} ({self.seat_type}): {self.status}, "
                f"Price: ${self.price:.2f}, "
                f"Last Maintenance: {self.last_maintenance_date or 'N/A'}")