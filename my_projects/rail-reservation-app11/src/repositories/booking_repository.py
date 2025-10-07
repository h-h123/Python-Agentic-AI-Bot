from typing import Dict, List, Optional
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.models.train import Train, Seat
from src.config.settings import settings

class BookingRepository:
    def __init__(self):
        self.bookings: Dict[str, Booking] = {}
        self.passengers: Dict[str, Passenger] = {}

    def save_booking(self, booking: Booking) -> Booking:
        """Save a booking to the repository"""
        self.bookings[booking.booking_id] = booking

        # Ensure passenger is also saved
        if booking.passenger.passenger_id not in self.passengers:
            self.passengers[booking.passenger.passenger_id] = booking.passenger

        return booking

    def find_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Find a booking by its ID"""
        return self.bookings.get(booking_id)

    def find_all_bookings(self) -> List[Booking]:
        """Get all bookings from the repository"""
        return list(self.bookings.values())

    def find_bookings_by_passenger(self, passenger_id: str) -> List[Booking]:
        """Find all bookings for a specific passenger"""
        return [booking for booking in self.bookings.values()
                if booking.passenger.passenger_id == passenger_id]

    def find_bookings_by_train(self, train_id: str) -> List[Booking]:
        """Find all bookings for a specific train"""
        return [booking for booking in self.bookings.values()
                if booking.train.train_id == train_id]

    def find_bookings_by_seat_class(self, seat_class: str) -> List[Booking]:
        """Find all bookings for a specific seat class"""
        return [booking for booking in self.bookings.values()
                if booking.seat.seat_class.lower() == seat_class.lower()]

    def update_booking(self, booking: Booking) -> Booking:
        """Update a booking in the repository"""
        if booking.booking_id not in self.bookings:
            raise ValueError(f"Booking with ID {booking.booking_id} not found")
        self.bookings[booking.booking_id] = booking
        return booking

    def delete_booking(self, booking_id: str) -> None:
        """Delete a booking from the repository"""
        if booking_id not in self.bookings:
            raise ValueError(f"Booking with ID {booking_id} not found")
        del self.bookings[booking_id]

    def save_passenger(self, passenger: Passenger) -> Passenger:
        """Save a passenger to the repository"""
        self.passengers[passenger.passenger_id] = passenger
        return passenger

    def find_passenger_by_id(self, passenger_id: str) -> Optional[Passenger]:
        """Find a passenger by their ID"""
        return self.passengers.get(passenger_id)

    def find_passenger_by_email(self, email: str) -> Optional[Passenger]:
        """Find a passenger by their email"""
        return next((p for p in self.passengers.values() if p.email == email), None)

    def find_passenger_by_phone(self, phone: str) -> Optional[Passenger]:
        """Find a passenger by their phone number"""
        return next((p for p in self.passengers.values() if p.phone == phone), None)

    def get_booking_occupancy_report(self) -> Dict[str, int]:
        """Generate a report of booking occupancy by seat class"""
        report = {seat_class: 0 for seat_class in settings.default_seat_classes}
        report['total'] = 0

        for booking in self.bookings.values():
            report[booking.seat.seat_class] += 1
            report['total'] += 1

        return report

    def get_passenger_booking_history(self, passenger_id: str) -> List[Dict]:
        """Get complete booking history for a passenger"""
        if passenger_id not in self.passengers:
            raise ValueError(f"Passenger with ID {passenger_id} not found")

        bookings = self.find_bookings_by_passenger(passenger_id)
        return [booking.get_booking_details() for booking in bookings]