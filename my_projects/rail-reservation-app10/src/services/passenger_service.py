from typing import Dict, List, Optional
from src.models import Passenger, Booking
from src.exceptions import BookingNotFoundError
from src.config.constants import (
    BOOKING_STATUS_CONFIRMED,
    ERROR_MESSAGES
)

class PassengerService:
    def __init__(self):
        self.passengers: Dict[str, Passenger] = {}

    def add_passenger(self, passenger_id: str, name: str, email: Optional[str] = None, phone: Optional[str] = None) -> Passenger:
        if passenger_id in self.passengers:
            raise ValueError(f"Passenger with ID {passenger_id} already exists")

        passenger = Passenger(
            passenger_id=passenger_id,
            name=name,
            email=email,
            phone=phone
        )
        self.passengers[passenger_id] = passenger
        return passenger

    def get_passenger(self, passenger_id: str) -> Optional[Passenger]:
        return self.passengers.get(passenger_id)

    def get_passenger_by_name(self, name: str) -> Optional[Passenger]:
        for passenger in self.passengers.values():
            if passenger.name.lower() == name.lower():
                return passenger
        return None

    def get_all_passengers(self) -> List[Passenger]:
        return list(self.passengers.values())

    def update_passenger_contact(self, passenger_id: str, email: Optional[str] = None, phone: Optional[str] = None) -> None:
        passenger = self.get_passenger(passenger_id)
        if not passenger:
            raise ValueError(f"Passenger with ID {passenger_id} not found")

        passenger.update_contact_info(email, phone)

    def add_booking_to_passenger(self, passenger_id: str, booking_id: str) -> None:
        passenger = self.get_passenger(passenger_id)
        if not passenger:
            raise ValueError(f"Passenger with ID {passenger_id} not found")

        passenger.add_booking(booking_id)

    def remove_booking_from_passenger(self, passenger_id: str, booking_id: str) -> None:
        passenger = self.get_passenger(passenger_id)
        if not passenger:
            raise ValueError(f"Passenger with ID {passenger_id} not found")

        passenger.remove_booking(booking_id)

    def get_passenger_bookings(self, passenger_id: str) -> List[str]:
        passenger = self.get_passenger(passenger_id)
        if not passenger:
            raise ValueError(f"Passenger with ID {passenger_id} not found")

        return passenger.get_booking_history()

    def get_passenger_loyalty_points(self, passenger_id: str) -> int:
        passenger = self.get_passenger(passenger_id)
        if not passenger:
            raise ValueError(f"Passenger with ID {passenger_id} not found")

        return passenger.loyalty_points

    def get_passenger_by_booking(self, booking_id: str) -> Optional[Passenger]:
        for passenger in self.passengers.values():
            if booking_id in passenger.get_booking_history():
                return passenger
        return None

    def delete_passenger(self, passenger_id: str) -> None:
        if passenger_id not in self.passengers:
            raise ValueError(f"Passenger with ID {passenger_id} not found")

        del self.passengers[passenger_id]