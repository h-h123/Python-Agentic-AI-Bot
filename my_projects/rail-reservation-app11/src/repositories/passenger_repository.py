from typing import Dict, List, Optional
from src.models.passenger import Passenger
from src.config.settings import settings

class PassengerRepository:
    def __init__(self):
        self.passengers: Dict[str, Passenger] = {}

    def save(self, passenger: Passenger) -> Passenger:
        """Save a passenger to the repository"""
        self.passengers[passenger.passenger_id] = passenger
        return passenger

    def find_by_id(self, passenger_id: str) -> Optional[Passenger]:
        """Find a passenger by their ID"""
        return self.passengers.get(passenger_id)

    def find_by_email(self, email: str) -> Optional[Passenger]:
        """Find a passenger by their email"""
        return next((p for p in self.passengers.values() if p.email == email), None)

    def find_by_phone(self, phone: str) -> Optional[Passenger]:
        """Find a passenger by their phone number"""
        return next((p for p in self.passengers.values() if p.phone == phone), None)

    def find_all(self) -> List[Passenger]:
        """Get all passengers from the repository"""
        return list(self.passengers.values())

    def update(self, passenger: Passenger) -> Passenger:
        """Update a passenger in the repository"""
        if passenger.passenger_id not in self.passengers:
            raise ValueError(f"Passenger with ID {passenger.passenger_id} not found")
        self.passengers[passenger.passenger_id] = passenger
        return passenger

    def delete(self, passenger_id: str) -> None:
        """Delete a passenger from the repository"""
        if passenger_id not in self.passengers:
            raise ValueError(f"Passenger with ID {passenger_id} not found")
        del self.passengers[passenger_id]

    def find_by_name(self, name: str) -> List[Passenger]:
        """Find passengers by name (partial match)"""
        return [p for p in self.passengers.values()
                if name.lower() in p.name.lower()]

    def get_passenger_booking_count(self, passenger_id: str) -> int:
        """Get the number of bookings for a passenger"""
        passenger = self.find_by_id(passenger_id)
        if not passenger:
            raise ValueError(f"Passenger with ID {passenger_id} not found")
        return len(passenger.bookings)

    def get_frequent_passengers(self, min_bookings: int = 3) -> List[Passenger]:
        """Get passengers with at least min_bookings bookings"""
        return [p for p in self.passengers.values()
                if len(p.bookings) >= min_bookings]

    def get_passenger_stats(self) -> Dict:
        """Get statistics about passengers in the system"""
        total_passengers = len(self.passengers)
        total_bookings = sum(len(p.bookings) for p in self.passengers.values())
        avg_bookings = total_bookings / total_passengers if total_passengers > 0 else 0

        return {
            "total_passengers": total_passengers,
            "total_bookings": total_bookings,
            "average_bookings_per_passenger": round(avg_bookings, 2),
            "most_common_seat_class": self._get_most_common_seat_class()
        }

    def _get_most_common_seat_class(self) -> str:
        """Helper method to get the most commonly booked seat class"""
        seat_class_counts = {seat_class: 0 for seat_class in settings.default_seat_classes}

        for passenger in self.passengers.values():
            for booking_id in passenger.bookings:
                # In a real implementation, we would look up the booking
                # This is simplified for the example
                pass

        # Return the seat class with the highest count
        return max(seat_class_counts.items(), key=lambda x: x[1])[0] if seat_class_counts else "Unknown"