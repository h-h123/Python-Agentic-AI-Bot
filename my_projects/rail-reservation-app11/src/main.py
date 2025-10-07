import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Train, Seat, Booking
from src.services import BookingService, TrainService
from datetime import datetime

def display_menu():
    print("\nRailway Reservation System")
    print("1. View Available Trains")
    print("2. Book a Seat")
    print("3. Cancel Booking")
    print("4. View Bookings")
    print("5. Exit")

def main():
    booking_service = BookingService()
    train_service = TrainService()

    # Initialize with sample data
    train1 = Train("T101", "Express", "New York", "Boston", datetime(2023, 12, 25, 14, 0), 100)
    train2 = Train("T102", "Local", "Chicago", "Detroit", datetime(2023, 12, 26, 9, 30), 50)
    train_service.add_train(train1)
    train_service.add_train(train2)

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            trains = train_service.get_all_trains()
            print("\nAvailable Trains:")
            for train in trains:
                print(f"ID: {train.train_id}, Name: {train.name}, Route: {train.source} to {train.destination}, "
                      f"Departure: {train.departure_time}, Available Seats: {train.available_seats}")

        elif choice == "2":
            train_id = input("Enter train ID: ")
            passenger_name = input("Enter passenger name: ")
            seat_class = input("Enter seat class (Economy/Business): ")

            try:
                booking = booking_service.book_seat(train_id, passenger_name, seat_class)
                print(f"\nBooking successful! Booking ID: {booking.booking_id}")
            except Exception as e:
                print(f"\nError: {str(e)}")

        elif choice == "3":
            booking_id = input("Enter booking ID to cancel: ")
            try:
                booking_service.cancel_booking(booking_id)
                print("\nBooking cancelled successfully!")
            except Exception as e:
                print(f"\nError: {str(e)}")

        elif choice == "4":
            bookings = booking_service.get_all_bookings()
            print("\nCurrent Bookings:")
            for booking in bookings:
                print(f"ID: {booking.booking_id}, Train: {booking.train.train_id}, "
                      f"Passenger: {booking.passenger_name}, Seat: {booking.seat.seat_number} ({booking.seat.seat_class})")

        elif choice == "5":
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


+++++ src/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import List
import uuid

@dataclass
class Seat:
    seat_number: str
    seat_class: str
    is_booked: bool = False

@dataclass
class Train:
    train_id: str
    name: str
    source: str
    destination: str
    departure_time: datetime
    total_seats: int
    available_seats: int = None
    seats: List[Seat] = None

    def __post_init__(self):
        if self.available_seats is None:
            self.available_seats = self.total_seats
        if self.seats is None:
            self.seats = [Seat(f"{i+1}", "Economy") for i in range(self.total_seats)]

@dataclass
class Booking:
    booking_id: str
    train: Train
    passenger_name: str
    seat: Seat
    booking_time: datetime = None

    def __post_init__(self):
        if self.booking_time is None:
            self.booking_time = datetime.now()


+++++ src/services.py
from src.models import Train, Seat, Booking
from typing import List, Dict
import uuid

class TrainService:
    def __init__(self):
        self.trains: Dict[str, Train] = {}

    def add_train(self, train: Train):
        self.trains[train.train_id] = train

    def get_train(self, train_id: str) -> Train:
        return self.trains.get(train_id)

    def get_all_trains(self) -> List[Train]:
        return list(self.trains.values())

class BookingService:
    def __init__(self):
        self.bookings: Dict[str, Booking] = {}
        self.train_service = TrainService()

    def book_seat(self, train_id: str, passenger_name: str, seat_class: str) -> Booking:
        train = self.train_service.get_train(train_id)
        if not train:
            raise ValueError("Train not found")

        if train.available_seats <= 0:
            raise ValueError("No available seats on this train")

        available_seat = None
        for seat in train.seats:
            if not seat.is_booked and seat.seat_class.lower() == seat_class.lower():
                available_seat = seat
                break

        if not available_seat:
            raise ValueError(f"No available {seat_class} seats")

        available_seat.is_booked = True
        train.available_seats -= 1

        booking = Booking(
            booking_id=str(uuid.uuid4()),
            train=train,
            passenger_name=passenger_name,
            seat=available_seat
        )

        self.bookings[booking.booking_id] = booking
        return booking

    def cancel_booking(self, booking_id: str):
        if booking_id not in self.bookings:
            raise ValueError("Booking not found")

        booking = self.bookings[booking_id]
        booking.seat.is_booked = False
        booking.train.available_seats += 1
        del self.bookings[booking_id]

    def get_all_bookings(self) -> List[Booking]:
        return list(self.bookings.values())