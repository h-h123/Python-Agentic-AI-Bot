from dataclasses import dataclass, field
from typing import List

@dataclass
class Passenger:
    passenger_id: str
    name: str
    booking_ids: List[str] = field(default_factory=list)

    def add_booking(self, booking_id: str) -> None:
        """Add a booking ID to the passenger's list of bookings."""
        if booking_id not in self.booking_ids:
            self.booking_ids.append(booking_id)

    def remove_booking(self, booking_id: str) -> bool:
        """Remove a booking ID from the passenger's list of bookings."""
        if booking_id in self.booking_ids:
            self.booking_ids.remove(booking_id)
            return True
        return False

    def get_bookings(self) -> List[str]:
        """Get all booking IDs associated with this passenger."""
        return self.booking_ids.copy()

    def has_bookings(self) -> bool:
        """Check if the passenger has any active bookings."""
        return len(self.booking_ids) > 0