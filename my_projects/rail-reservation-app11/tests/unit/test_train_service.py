import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from src.models.train import Train, Seat
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.services.train_service import TrainService
from src.utils.exceptions import (
    TrainNotFoundError,
    SeatNotAvailableError,
    BookingNotFoundError,
    InvalidSeatClassError
)

class TestTrainService:
    """Test cases for the TrainService."""

    @pytest.fixture
    def train_service(self):
        """Create a TrainService instance for testing."""
        return TrainService()

    @pytest.fixture
    def sample_train(self):
        """Create a sample train for testing."""
        departure_time = datetime.now() + timedelta(days=1)
        return Train(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=departure_time,
            total_seats=100
        )

    def test_add_train(self, train_service, sample_train):
        """Test adding a train to the service."""
        train_service.add_train(sample_train)
        assert sample_train.train_id in train_service.trains
        assert train_service.trains[sample_train.train_id] == sample_train

    def test_get_train(self, train_service, sample_train):
        """Test getting a train by ID."""
        train_service.add_train(sample_train)
        retrieved_train = train_service.get_train(sample_train.train_id)
        assert retrieved_train == sample_train

    def test_get_train_not_found(self, train_service):
        """Test getting a non-existent train."""
        with pytest.raises(TrainNotFoundError):
            train_service.get_train("NONEXISTENT")

    def test_get_all_trains(self, train_service, sample_train):
        """Test getting all trains."""
        train_service.add_train(sample_train)
        trains = train_service.get_all_trains()
        assert len(trains) == 1
        assert sample_train in trains

    def test_update_train(self, train_service, sample_train):
        """Test updating train information."""
        train_service.add_train(sample_train)

        # Update some attributes
        updated_train = train_service.update_train(
            sample_train.train_id,
            name="Super Express",
            total_seats=120
        )

        assert updated_train.name == "Super Express"
        assert updated_train.total_seats == 120

    def test_remove_train(self, train_service, sample_train):
        """Test removing a train from the service."""
        train_service.add_train(sample_train)
        train_service.remove_train(sample_train.train_id)
        assert sample_train.train_id not in train_service.trains

    def test_get_available_seats(self, train_service, sample_train):
        """Test getting available seats for a train."""
        train_service.add_train(sample_train)
        available_seats = train_service.get_available_seats(sample_train.train_id)
        assert len(available_seats) == 100  # All seats should be available initially

    def test_get_train_seat_map(self, train_service, sample_train):
        """Test getting seat map for a train."""
        train_service.add_train(sample_train)
        seat_map = train_service.get_train_seat_map(sample_train.train_id)

        assert "Economy" in seat_map
        assert "Business" in seat_map
        assert len(seat_map["Economy"]) == 80  # 80% of 100
        assert len(seat_map["Business"]) == 20  # 20% of 100

    def test_get_train_occupancy(self, train_service, sample_train):
        """Test getting occupancy percentage for a train."""
        train_service.add_train(sample_train)
        occupancy = train_service.get_train_occupancy(sample_train.train_id)
        assert occupancy == 0.0  # No seats booked initially

    def test_search_trains(self, train_service, sample_train):
        """Test searching trains by criteria."""
        train_service.add_train(sample_train)

        # Search by source
        trains = train_service.search_trains(source="New York")
        assert len(trains) == 1
        assert trains[0] == sample_train

        # Search by non-existent destination
        trains = train_service.search_trains(destination="Chicago")
        assert len(trains) == 0

    def test_get_train_seat_map_with_booked_seats(self, train_service, sample_train):
        """Test getting seat map for a train with some booked seats."""
        train_service.add_train(sample_train)

        # Book some seats
        for i in range(5):
            seat = sample_train.seats[i]
            seat.is_booked = True
            sample_train.available_seats -= 1

        seat_map = train_service.get_train_seat_map(sample_train.train_id)

        # Verify the seat map reflects booked seats
        booked_seats_in_map = 0
        for seat_class, seats in seat_map.items():
            for seat in seats:
                if seat["is_booked"]:
                    booked_seats_in_map += 1

        assert booked_seats_in_map == 5

    def test_get_available_seats_by_class(self, train_service, sample_train):
        """Test getting available seats filtered by class."""
        train_service.add_train(sample_train)

        # Book some economy seats
        for i in range(10):
            seat = sample_train.seats[i]
            if seat.seat_class == "Economy":
                seat.is_booked = True
                sample_train.available_seats -= 1

        available_economy = train_service.get_available_seats(sample_train.train_id, "Economy")
        available_business = train_service.get_available_seats(sample_train.train_id, "Business")

        assert len(available_economy) == 70  # 80 - 10 booked
        assert len(available_business) == 20  # All business seats available

    def test_update_train_with_invalid_data(self, train_service, sample_train):
        """Test updating train with invalid data."""
        train_service.add_train(sample_train)

        # Try to update with invalid data
        with pytest.raises(ValueError):
            train_service.update_train(
                sample_train.train_id,
                total_seats=-10
            )