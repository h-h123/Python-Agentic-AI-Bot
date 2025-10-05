from dataclasses import dataclass
from typing import Optional

@dataclass
class Passenger:
    passenger_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    booking_history: list = None

    def __post_init__(self):
        if self.booking_history is None:
            self.booking_history = []

    def add_booking(self, train_id: str, seat_number: int, booking_date: str):
        self.booking_history.append({
            'train_id': train_id,
            'seat_number': seat_number,
            'booking_date': booking_date,
            'status': 'active'
        })

    def cancel_booking(self, train_id: str, seat_number: int):
        for booking in self.booking_history:
            if (booking['train_id'] == train_id and
                booking['seat_number'] == seat_number and
                booking['status'] == 'active'):
                booking['status'] = 'cancelled'
                return True
        return False

    def get_active_bookings(self):
        return [booking for booking in self.booking_history if booking['status'] == 'active']

    def get_booking_history(self):
        return self.booking_history.copy()

class PassengerService:
    def __init__(self):
        self.passengers = {}

    def create_passenger(self, passenger_id: str, name: str, email: Optional[str] = None, phone: Optional[str] = None):
        if passenger_id in self.passengers:
            return None

        passenger = Passenger(passenger_id=passenger_id, name=name, email=email, phone=phone)
        self.passengers[passenger_id] = passenger
        return passenger

    def get_passenger(self, passenger_id: str):
        return self.passengers.get(passenger_id)

    def update_passenger(self, passenger_id: str, **kwargs):
        passenger = self.get_passenger(passenger_id)
        if not passenger:
            return False

        for key, value in kwargs.items():
            if hasattr(passenger, key):
                setattr(passenger, key, value)
        return True

    def delete_passenger(self, passenger_id: str):
        if passenger_id in self.passengers:
            del self.passengers[passenger_id]
            return True
        return False