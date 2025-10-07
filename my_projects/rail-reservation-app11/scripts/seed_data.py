import os
import uuid
from datetime import datetime, timedelta
from src.models.train import Train
from src.models.seat import Seat
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.services.train_service import TrainService
from src.services.booking_service import BookingService

def seed_trains(train_service: TrainService):
    """Seed the system with sample trains."""
    trains = [
        Train(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=datetime.now() + timedelta(days=7),
            total_seats=100
        ),
        Train(
            train_id="T102",
            name="Local",
            source="Chicago",
            destination="Detroit",
            departure_time=datetime.now() + timedelta(days=3),
            total_seats=50
        ),
        Train(
            train_id="T103",
            name="Regional",
            source="Seattle",
            destination="Portland",
            departure_time=datetime.now() + timedelta(days=14),
            total_seats=75
        ),
        Train(
            train_id="T104",
            name="Night Express",
            source="Los Angeles",
            destination="San Francisco",
            departure_time=datetime.now() + timedelta(days=2),
            total_seats=120
        ),
        Train(
            train_id="T105",
            name="Scenic Route",
            source="Denver",
            destination="Aspen",
            departure_time=datetime.now() + timedelta(days=10),
            total_seats=60
        )
    ]

    for train in trains:
        train_service.add_train(train)

def seed_bookings(booking_service: BookingService):
    """Seed the system with sample bookings."""
    passenger_names = [
        "John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis", "Robert Wilson",
        "Jennifer Taylor", "David Anderson", "Jessica Martinez", "Thomas Lee", "Lisa White"
    ]

    # Book seats on different trains
    for i, name in enumerate(passenger_names):
        train_id = f"T10{(i % 5) + 1}"  # Distribute across 5 trains
        seat_class = "Economy" if i % 2 == 0 else "Business"

        booking_service.book_seat(
            train_id=train_id,
            passenger_name=name,
            seat_class=seat_class,
            email=f"{name.lower().replace(' ', '.')}@example.com",
            phone=f"+1555{i:03d}0000"
        )

def seed_data():
    """Seed the entire system with sample data."""
    train_service = TrainService()
    booking_service = BookingService()

    # Clear existing data
    train_service.trains.clear()
    booking_service.bookings.clear()

    # Seed trains and bookings
    seed_trains(train_service)
    seed_bookings(booking_service)

    print(f"Seeded {len(train_service.get_all_trains())} trains")
    print(f"Seeded {len(booking_service.get_all_bookings())} bookings")

if __name__ == "__main__":
    seed_data()