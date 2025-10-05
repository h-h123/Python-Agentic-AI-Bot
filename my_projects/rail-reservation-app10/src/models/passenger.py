from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from src.config.constants import (
    DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT,
    MAX_BOOKINGS_PER_PASSENGERS
)

@dataclass
class Passenger:
    passenger_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    bookings: List[str] = field(default_factory=list)
    registration_date: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))
    loyalty_points: int = 0

    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Passenger name must be a non-empty string")

        if not self.passenger_id or not isinstance(self.passenger_id, str):
            raise ValueError("Passenger ID must be a non-empty string")

        if self.email and not self._validate_email(self.email):
            raise ValueError("Invalid email format")

        if self.phone and not self._validate_phone(self.phone):
            raise ValueError("Invalid phone number format")

    @staticmethod
    def _validate_email(email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]

    @staticmethod
    def _validate_phone(phone: str) -> bool:
        return phone.isdigit() and len(phone) >= 10

    def add_booking(self, booking_id: str) -> None:
        if len(self.bookings) >= MAX_BOOKINGS_PER_PASSENGERS:
            raise ValueError(f"Maximum {MAX_BOOKINGS_PER_PASSENGERS} bookings allowed per passenger")

        if booking_id in self.bookings:
            raise ValueError(f"Booking {booking_id} already exists for this passenger")

        self.bookings.append(booking_id)
        self.loyalty_points += 10

    def remove_booking(self, booking_id: str) -> None:
        if booking_id not in self.bookings:
            raise ValueError(f"Booking {booking_id} not found for this passenger")

        self.bookings.remove(booking_id)
        self.loyalty_points = max(0, self.loyalty_points - 5)

    def get_booking_history(self) -> List[str]:
        return self.bookings.copy()

    def update_contact_info(self, email: Optional[str] = None, phone: Optional[str] = None) -> None:
        if email is not None:
            if not self._validate_email(email):
                raise ValueError("Invalid email format")
            self.email = email

        if phone is not None:
            if not self._validate_phone(phone):
                raise ValueError("Invalid phone number format")
            self.phone = phone

    def __str__(self) -> str:
        return (f"Passenger {self.passenger_id}: {self.name}, "
                f"Email: {self.email or 'N/A'}, "
                f"Phone: {self.phone or 'N/A'}, "
                f"Loyalty Points: {self.loyalty_points}")