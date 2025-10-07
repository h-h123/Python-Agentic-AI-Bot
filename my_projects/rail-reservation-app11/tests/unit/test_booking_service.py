import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from src.models.train import Train, Seat
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.services.booking_service import BookingService
from src.utils.exceptions import (
    TrainNotFoundError,
    SeatNotAvailableError,
    BookingNotFoundError,
    InvalidSeatClassError
)

class TestBookingService:
    """Test cases for the BookingService."""

    @pytest.fixture
    def booking_service(self):
        """Create a BookingService instance for testing."""
        return BookingService()

    @pytest.fixture
    def sample_train(self):
        """Create a sample train for testing."""
        departure_time = datetime.now() + timedelta(days=1)
        train = Train(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=departure_time,
            total_seats=100
        )
        return train

    def test_book_seat_success(self, booking_service, sample_train):
        """Test successful seat booking."""
        booking_service.train_service.trains[sample_train.train_id] = sample_train

        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy"
        )

        assert booking.booking_id is not None
        assert booking.train == sample_train
        assert booking.passenger.name == "John Doe"
        assert booking.seat.seat_class == "Economy"
        assert booking.seat.is_booked is True
        assert sample_train.available_seats == 99

    def test_book_seat_train_not_found(self, booking_service):
        """Test booking a seat for non-existent train."""
        with pytest.raises(TrainNotFoundError):
            booking_service.book_seat(
                train_id="NONEXISTENT",
                passenger_name="John Doe",
                seat_class="Economy"
            )

    def test_book_seat_no_available_seats(self, booking_service, sample_train):
        """Test booking a seat when no seats are available."""
        booking_service.train_service.trains[sample_train.train_id] = sample_train

        # Book all seats first
        for _ in range(100):
            booking_service.book_seat(
                train_id=sample_train.train_id,
                passenger_name=f"Passenger {_}",
                seat_class="Economy"
            )

        # Try to book one more
        with pytest.raises(SeatNotAvailableError):
            booking_service.book_seat(
                train_id=sample_train.train_id,
                passenger_name="John Doe",
                seat_class="Economy"
            )

    def test_book_seat_invalid_class(self, booking_service, sample_train):
        """Test booking a seat with invalid class."""
        booking_service.train_service.trains[sample_train.train_id] = sample_train

        with pytest.raises(InvalidSeatClassError):
            booking_service.book_seat(
                train_id=sample_train.train_id,
                passenger_name="John Doe",
                seat_class="First"
            )

    def test_cancel_booking_success(self, booking_service, sample_train):
        """Test successful booking cancellation."""
        booking_service.train_service.trains[sample_train.train_id] = sample_train

        # First create a booking
        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy"
        )

        # Then cancel it
        booking_details = booking_service.cancel_booking(booking.booking_id)

        assert booking_details["status"] == "cancelled"
        assert booking_details["seat_number"] == booking.seat.seat_number
        assert sample_train.available_seats == 100  # Seat should be available again

    def test_cancel_booking_not_found(self, booking_service):
        """Test cancelling a non-existent booking."""
        with pytest.raises(BookingNotFoundError):
            booking_service.cancel_booking("NONEXISTENT")

    def test_get_booking_success(self, booking_service, sample_train):
        """Test getting a booking by ID."""
        booking_service.train_service.trains[sample_train.train_id] = sample_train

        # First create a booking
        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy"
        )

        # Then retrieve it
        retrieved_booking = booking_service.get_booking(booking.booking_id)
        assert retrieved_booking == booking

    def test_get_booking_not_found(self, booking_service):
        """Test getting a non-existent booking."""
        with pytest.raises(BookingNotFoundError):
            booking_service.get_booking("NONEXISTENT")

    def test_get_all_bookings(self, booking_service, sample_train):
        """Test getting all bookings."""
        booking_service.train_service.trains[sample_train.train_id] = sample_train

        # Create multiple bookings
        booking1 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy"
        )

        booking2 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Jane Smith",
            seat_class="Business"
        )

        bookings = booking_service.get_all_bookings()
        assert len(bookings) == 2
        assert booking1 in bookings
        assert booking2 in bookings

    def test_get_bookings_by_passenger(self, booking_service, sample_train):
        """Test getting bookings by passenger."""
        booking_service.train_service.trains[sample_train.train_id] = sample_train

        # Create bookings for the same passenger
        booking1 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy"
        )

        booking2 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Business"
        )

        # Create a booking for a different passenger
        booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Jane Smith",
            seat_class="Economy"
        )

        # Get bookings for John Doe
        john_bookings = booking_service.get_bookings_by_passenger(booking1.passenger.passenger_id)
        assert len(john_bookings) == 2
        assert booking1 in john_bookings
        assert booking2 in john_bookings

    def test_get_bookings_by_train(self, booking_service, sample_train):
        """Test getting bookings by train."""
        booking_service.train_service.trains[sample_train.train_id] = sample_train

        # Create bookings for the same train
        booking1 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy"
        )

        booking2 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Jane Smith",
            seat_class="Business"
        )

        # Get bookings for the train
        train_bookings = booking_service.get_bookings_by_train(sample_train.train_id)
        assert len(train_bookings) == 2
        assert booking1 in train_bookings
        assert booking2 in train_bookings

    def test_get_payment_receipt(self, booking_service, sample_train):
        """Test getting a payment receipt for a booking."""
        booking_service.train_service.trains[sample_train.train_id] = sample_train

        # Create a booking
        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy"
        )

        # Get the receipt
        receipt = booking_service.get_payment_receipt(booking.booking_id)
        assert "Booking ID:" in receipt
        assert "Payment ID:" in receipt
        assert "Amount:" in receipt