# tests/__init__.py

"""
Test package for the Railway Reservation System.

This package contains all unit tests, integration tests, and functional tests
for the railway reservation system application.
"""

from . import (
    test_models,
    test_services,
    test_utils,
    test_api,
    test_cli
)

__all__ = [
    "test_models",
    "test_services",
    "test_utils",
    "test_api",
    "test_cli"
]


+++++ tests/test_models.py
"""
Unit tests for the models in the Railway Reservation System.
"""

import pytest
from datetime import datetime, timedelta
from src.models.train import Train, Seat
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.models.payment import Payment, PaymentMethod, PaymentStatus

class TestSeatModel:
    """Test cases for the Seat model."""

    def test_seat_creation(self):
        """Test creating a seat with valid parameters."""
        seat = Seat(seat_number="1A", seat_class="Economy")
        assert seat.seat_number == "1A"
        assert seat.seat_class == "Economy"
        assert seat.is_booked is False
        assert seat.price > 0

    def test_seat_price_by_class(self):
        """Test that seat price is set correctly based on class."""
        economy_seat = Seat(seat_number="1A", seat_class="Economy")
        business_seat = Seat(seat_number="1B", seat_class="Business")

        assert economy_seat.price < business_seat.price

    def test_seat_booking_status(self):
        """Test changing seat booking status."""
        seat = Seat(seat_number="1A", seat_class="Economy")
        assert seat.is_booked is False

        seat.is_booked = True
        assert seat.is_booked is True

class TestTrainModel:
    """Test cases for the Train model."""

    def test_train_creation(self):
        """Test creating a train with valid parameters."""
        departure_time = datetime.now() + timedelta(days=1)
        train = Train(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=departure_time,
            total_seats=100
        )

        assert train.train_id == "T101"
        assert train.name == "Express"
        assert train.source == "New York"
        assert train.destination == "Boston"
        assert train.departure_time == departure_time
        assert train.total_seats == 100
        assert train.available_seats == 100
        assert len(train.seats) == 100

    def test_train_seat_distribution(self):
        """Test that train seats are correctly distributed between classes."""
        train = Train(
            train_id="T102",
            name="Local",
            source="Chicago",
            destination="Detroit",
            departure_time=datetime.now() + timedelta(days=2),
            total_seats=50
        )

        economy_seats = [seat for seat in train.seats if seat.seat_class == "Economy"]
        business_seats = [seat for seat in train.seats if seat.seat_class == "Business"]

        assert len(economy_seats) == 40  # 80% of 50
        assert len(business_seats) == 10  # 20% of 50

    def test_get_available_seats_by_class(self):
        """Test getting available seats by class."""
        train = Train(
            train_id="T103",
            name="Regional",
            source="Seattle",
            destination="Portland",
            departure_time=datetime.now() + timedelta(days=3),
            total_seats=20
        )

        available_economy = train.get_available_seats_by_class("Economy")
        available_business = train.get_available_seats_by_class("Business")

        assert len(available_economy) == 16  # 80% of 20
        assert len(available_business) == 4  # 20% of 20

class TestPassengerModel:
    """Test cases for the Passenger model."""

    def test_passenger_creation(self):
        """Test creating a passenger with valid parameters."""
        passenger = Passenger(
            passenger_id="P101",
            name="John Doe",
            email="john@example.com",
            phone="+1234567890"
        )

        assert passenger.passenger_id == "P101"
        assert passenger.name == "John Doe"
        assert passenger.email == "john@example.com"
        assert passenger.phone == "+1234567890"
        assert passenger.bookings == []

    def test_add_remove_booking(self):
        """Test adding and removing bookings from passenger."""
        passenger = Passenger(passenger_id="P102", name="Jane Smith")

        passenger.add_booking("B101")
        assert "B101" in passenger.bookings

        passenger.remove_booking("B101")
        assert "B101" not in passenger.bookings

class TestBookingModel:
    """Test cases for the Booking model."""

    def test_booking_creation(self):
        """Test creating a booking with valid parameters."""
        departure_time = datetime.now() + timedelta(days=1)
        train = Train(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=departure_time,
            total_seats=100
        )

        passenger = Passenger(passenger_id="P101", name="John Doe")
        seat = train.seats[0]

        booking = Booking(
            booking_id="B101",
            train=train,
            passenger=passenger,
            seat=seat
        )

        assert booking.booking_id == "B101"
        assert booking.train == train
        assert booking.passenger == passenger
        assert booking.seat == seat
        assert booking.status == "confirmed"
        assert booking.booking_time is not None

    def test_booking_cancellation(self):
        """Test cancelling a booking."""
        departure_time = datetime.now() + timedelta(days=1)
        train = Train(
            train_id="T102",
            name="Local",
            source="Chicago",
            destination="Detroit",
            departure_time=departure_time,
            total_seats=50
        )

        passenger = Passenger(passenger_id="P102", name="Jane Smith")
        seat = train.seats[0]
        seat.is_booked = True
        train.available_seats = 49

        booking = Booking(
            booking_id="B102",
            train=train,
            passenger=passenger,
            seat=seat
        )

        booking.cancel()

        assert booking.status == "cancelled"
        assert seat.is_booked is False
        assert train.available_seats == 50
        assert booking.cancellation_fee is not None

    def test_get_booking_details(self):
        """Test getting booking details as a dictionary."""
        departure_time = datetime.now() + timedelta(days=1)
        train = Train(
            train_id="T103",
            name="Regional",
            source="Seattle",
            destination="Portland",
            departure_time=departure_time,
            total_seats=20
        )

        passenger = Passenger(passenger_id="P103", name="Bob Johnson")
        seat = train.seats[0]

        booking = Booking(
            booking_id="B103",
            train=train,
            passenger=passenger,
            seat=seat
        )

        details = booking.get_booking_details()

        assert details["booking_id"] == "B103"
        assert details["train_id"] == "T103"
        assert details["passenger_name"] == "Bob Johnson"
        assert details["seat_number"] == seat.seat_number
        assert details["seat_class"] == seat.seat_class
        assert details["status"] == "confirmed"

class TestPaymentModel:
    """Test cases for the Payment model."""

    def test_payment_creation(self):
        """Test creating a payment with valid parameters."""
        payment = Payment(
            payment_id="PAY101",
            booking_id="B101",
            amount=50.00,
            currency="USD",
            payment_method=PaymentMethod.CREDIT_CARD
        )

        assert payment.payment_id == "PAY101"
        assert payment.booking_id == "B101"
        assert payment.amount == 50.00
        assert payment.currency == "USD"
        assert payment.payment_method == PaymentMethod.CREDIT_CARD
        assert payment.status == PaymentStatus.PENDING
        assert payment.payment_time is not None
        assert payment.transaction_reference is not None

    def test_payment_processing(self):
        """Test processing a payment."""
        payment = Payment(
            payment_id="PAY102",
            booking_id="B102",
            amount=75.00,
            currency="USD",
            payment_method=PaymentMethod.PAYPAL
        )

        result = payment.process_payment()
        assert result is True
        assert payment.status == PaymentStatus.COMPLETED

    def test_payment_refund(self):
        """Test refunding a payment."""
        payment = Payment(
            payment_id="PAY103",
            booking_id="B103",
            amount=100.00,
            currency="USD",
            payment_method=PaymentMethod.DEBIT_CARD
        )

        # First complete the payment
        payment.process_payment()

        # Then refund it
        result = payment.refund(50.00)
        assert result is True
        assert payment.status == PaymentStatus.REFUNDED
        assert payment.refund_amount == 50.00
        assert payment.refund_time is not None

    def test_get_payment_details(self):
        """Test getting payment details as a dictionary."""
        payment = Payment(
            payment_id="PAY104",
            booking_id="B104",
            amount=120.00,
            currency="USD",
            payment_method=PaymentMethod.BANK_TRANSFER
        )

        details = payment.get_payment_details()

        assert details["payment_id"] == "PAY104"
        assert details["booking_id"] == "B104"
        assert details["amount"] == 120.00
        assert details["currency"] == "USD"
        assert details["payment_method"] == "Bank Transfer"
        assert details["status"] == "PENDING"
        assert details["payment_time"] == payment.payment_time.isoformat()


+++++ tests/test_services.py
"""
Unit tests for the services in the Railway Reservation System.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from src.models.train import Train, Seat
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.models.payment import Payment, PaymentMethod, PaymentStatus
from src.services.booking_service import BookingService
from src.services.train_service import TrainService
from src.services.payment_service import PaymentService
from src.utils.exceptions import (
    TrainNotFoundError,
    SeatNotAvailableError,
    BookingNotFoundError,
    PaymentProcessingError
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

class TestBookingService:
    """Test cases for the BookingService."""

    @pytest.fixture
    def booking_service(self):
        """Create a BookingService instance for testing."""
        return BookingService()

    @pytest.fixture
    def train_service(self):
        """Create a TrainService instance for testing."""
        return TrainService()

    @pytest.fixture
    def sample_train(self, train_service):
        """Create and add a sample train for testing."""
        departure_time = datetime.now() + timedelta(days=1)
        train = Train(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=departure_time,
            total_seats=100
        )
        train_service.add_train(train)
        return train

    def test_book_seat(self, booking_service, sample_train):
        """Test booking a seat."""
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

    def test_book_seat_not_available(self, booking_service, sample_train):
        """Test booking a seat when none are available."""
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
        with pytest.raises(InvalidSeatClassError):
            booking_service.book_seat(
                train_id=sample_train.train_id,
                passenger_name="John Doe",
                seat_class="First"
            )

    def test_cancel_booking(self, booking_service, sample_train):
        """Test cancelling a booking."""
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

    def test_get_booking(self, booking_service, sample_train):
        """Test getting a booking by ID."""
        # First create a booking
        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy"
        )

        # Then retrieve it
        retrieved_booking = booking_service.get_booking(booking.booking_id)
        assert retrieved_booking == booking

    def test_get_all_bookings(self, booking_service, sample_train):
        """Test getting all bookings."""
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

class TestPaymentService:
    """Test cases for the PaymentService."""

    @pytest.fixture
    def payment_service(self):
        """Create a PaymentService instance for testing."""
        return PaymentService()

    @pytest.fixture
    def sample_booking(self, sample_train):
        """Create a sample booking for testing."""
        passenger = Passenger(passenger_id="P101", name="John Doe")
        seat = sample_train.seats[0]
        seat.is_booked = True
        sample_train.available_seats = 99

        return Booking(
            booking_id="B101",
            train=sample_train,
            passenger=passenger,
            seat=seat
        )

    def test_create_payment(self, payment_service, sample_booking):
        """Test creating a payment for a booking."""
        payment = payment_service.create_payment(
            booking=sample_booking,
            payment_method=PaymentMethod.CREDIT_CARD
        )

        assert payment.payment_id is not None
        assert payment.booking_id == sample_booking.booking_id
        assert payment.amount == sample_booking.seat.price
        assert payment.payment_method == PaymentMethod.CREDIT_CARD
        assert payment.status == PaymentStatus.PENDING

    def test_process_payment(self, payment_service, sample_booking):
        """Test processing a payment."""
        # First create a payment
        payment = payment_service.create_payment(
            booking=sample_booking,
            payment_method=PaymentMethod.PAYPAL
        )

        # Then process it
        result = payment_service.process_payment(payment.payment_id)
        assert result is True
        assert payment.status == PaymentStatus.COMPLETED

    def test_process_payment_not_found(self, payment_service):
        """Test processing a non-existent payment."""
        with pytest.raises(PaymentProcessingError):
            payment_service.process_payment("NONEXISTENT")

    def test_refund_payment(self, payment_service, sample_booking):
        """Test refunding a payment."""
        # Create and complete a payment
        payment = payment_service.create_payment(
            booking=sample_booking,
            payment_method=PaymentMethod.DEBIT_CARD
        )
        payment_service.process_payment(payment.payment_id)

        # Then refund it
        result = payment_service.refund_payment(payment.payment_id, 50.00)
        assert result is True
        assert payment.status == PaymentStatus.REFUNDED
        assert payment.refund_amount == 50.00
        assert payment.refund_time is not None

    def test_get_payment(self, payment_service, sample_booking):
        """Test getting a payment by ID."""
        # Create a payment
        payment = payment_service.create_payment(
            booking=sample_booking,
            payment_method=PaymentMethod.BANK_TRANSFER
        )

        # Then retrieve it
        retrieved_payment = payment_service.get_payment(payment.payment_id)
        assert retrieved_payment == payment

    def test_get_payment_not_found(self, payment_service):
        """Test getting a non-existent payment."""
        with pytest.raises(PaymentProcessingError):
            payment_service.get_payment("NONEXISTENT")

    def test_get_payments_by_booking(self, payment_service, sample_booking):
        """Test getting payments by booking ID."""
        # Create multiple payments for the same booking
        payment1 = payment_service.create_payment(
            booking=sample_booking,
            payment_method=PaymentMethod.CREDIT_CARD
        )

        payment2 = payment_service.create_payment(
            booking=sample_booking,
            payment_method=PaymentMethod.PAYPAL
        )

        # Get payments for the booking
        booking_payments = payment_service.get_payments_by_booking(sample_booking.booking_id)
        assert len(booking_payments) == 2
        assert payment1 in booking_payments
        assert payment2 in booking_payments

    def test_generate_receipt(self, payment_service, sample_booking):
        """Test generating a payment receipt."""
        # Create and complete a payment
        payment = payment_service.create_payment(
            booking=sample_booking,
            payment_method=PaymentMethod.MOBILE_WALLET
        )
        payment_service.process_payment(payment.payment_id)

        # Generate receipt
        receipt_content = payment_service.generate_receipt(payment.payment_id)
        assert "PAYMENT RECEIPT" in receipt_content
        assert "Payment ID:" in receipt_content
        assert "Amount:" in receipt_content

    def test_get_receipt(self, payment_service, sample_booking):
        """Test getting a payment receipt by ID."""
        # Create and complete a payment
        payment = payment_service.create_payment(
            booking=sample_booking,
            payment_method=PaymentMethod.CREDIT_CARD
        )
        payment_service.process_payment(payment.payment_id)

        # Generate and get receipt
        receipt_content = payment_service.generate_receipt(payment.payment_id)
        receipt = payment_service.get_receipt(payment.payment_id)

        assert receipt.receipt_id is not None
        assert receipt.payment == payment
        assert receipt.issued_time is not None
        assert receipt.generate_receipt() == receipt_content

    def test_get_payment_status(self, payment_service, sample_booking):
        """Test getting payment status."""
        # Create a payment
        payment = payment_service.create_payment(
            booking=sample_booking,
            payment_method=PaymentMethod.DEBIT_CARD
        )

        # Check initial status
        status = payment_service.get_payment_status(payment.payment_id)
        assert status == PaymentStatus.PENDING

        # Process payment and check status again
        payment_service.process_payment(payment.payment_id)
        status = payment_service.get_payment_status(payment.payment_id)
        assert status == PaymentStatus.COMPLETED

    def test_calculate_cancellation_fee(self, payment_service, sample_booking):
        """Test calculating cancellation fee for a booking."""
        fee = payment_service.calculate_cancellation_fee(sample_booking)
        expected_fee = sample_booking.seat.price * 0.10  # 10% cancellation fee
        assert fee == expected_fee


+++++ tests/test_utils.py
"""
Unit tests for the utility functions in the Railway Reservation System.
"""

import pytest
from datetime import datetime, timedelta
from src.utils.validators import (
    validate_email,
    validate_phone,
    validate_passenger_name,
    validate_train_id,
    validate_booking_id,
    validate_seat_class,
    validate_payment_method,
    validate_seat_availability,
    validate_date_format,
    validate_time_format,
    validate_departure_time,
    validate_positive_number,
    validate_price,
    validate_booking_data,
    validate_train_data
)
from src.utils.exceptions import ValidationError
from src.models.train import Seat

class TestValidationUtils:
    """Test cases for validation utility functions."""

    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@sub.domain.co.uk") is True

        # Invalid emails
        assert validate_email("invalid") is False
        assert validate_email("missing@at.com.") is False
        assert validate_email("no@tld") is False

    def test_validate_phone(self):
        """Test phone number validation."""
        # Valid phone numbers
        assert validate_phone("+1234567890") is True
        assert validate_phone("123-456-7890") is True
        assert validate_phone("(123) 456-7890") is True
        assert validate_phone("12345678") is True  # Minimum 8 digits

        # Invalid phone numbers
        assert validate_phone("123") is False  # Too short
        assert validate_phone("abcdefghij") is False  # No digits
        assert validate_phone("") is False  # Empty

    def test_validate_passenger_name(self):
        """Test passenger name validation."""
        # Valid names
        assert validate_passenger_name("John Doe") is True
        assert validate_passenger_name("Jean-Luc Picard") is True
        assert validate_passenger_name("O'Connor") is True

        # Invalid names
        assert validate_passenger_name("A") is False  # Too short
        assert validate_passenger_name("John123") is False  # Contains numbers
        assert validate_passenger_name("") is False  # Empty
        assert validate_passenger_name("  ") is False  # Whitespace only

    def test_validate_train_id(self):
        """Test train ID validation."""
        # Valid train IDs
        assert validate_train_id("T101") is True
        assert validate_train_id("EXP202") is True
        assert validate_train_id("A1") is True

        # Invalid train IDs
        assert validate_train_id("101") is False  # No letters
        assert validate_train_id("T101A") is False  # Letters in wrong place
        assert validate_train_id("T-101") is False  # Invalid character
        assert validate_train_id("") is False  # Empty

    def test_validate_booking_id(self):
        """Test booking ID validation (UUID format)."""
        # Valid UUIDs
        assert validate_booking_id("123e4567-e89b-12d3-a456-426614174000") is True
        assert validate_booking_id("550e8400-e29b-41d4-a716-446655440000") is True

        # Invalid UUIDs
        assert validate_booking_id("123e4567e89b12d3a456426614174000") is False  # Missing hyphens
        assert validate_booking_id("123e4567-e89b-12d3-a456-42661417400") is False  # Too short
        assert validate_booking_id("not-a-uuid") is False  # Not a UUID
        assert validate_booking_id("") is False  # Empty

    def test_validate_seat_class(self):
        """Test seat class validation."""
        # Valid seat classes (assuming default classes are Economy and Business)
        assert validate_seat_class("Economy") is True
        assert validate_seat_class("Business") is True
        assert validate_seat_class("economy") is True  # Case insensitive

        # Invalid seat classes
        assert validate_seat_class("First") is False
        assert validate_seat_class("Premium") is False
        assert validate_seat_class("") is False  # Empty

    def test_validate_payment_method(self):
        """Test payment method validation."""
        # Valid payment methods
        assert validate_payment_method("credit_card") is True
        assert validate_payment_method("debit_card") is True
        assert validate_payment_method("paypal") is True
        assert validate_payment_method("bank_transfer") is True
        assert validate_payment_method("mobile_wallet") is True

        # Invalid payment methods
        assert validate_payment_method("cash") is False
        assert validate_payment_method("check") is False
        assert validate_payment_method("") is False  # Empty

    def test_validate_seat_availability(self):
        """Test seat availability validation."""
        # Create some seats
        available_seats = [
            Seat("1A", "Economy", False),
            Seat("2A", "Business", False)
        ]

        booked_seats = [
            Seat("1A", "Economy", True),
            Seat("2A", "Business", True)
        ]

        # Test with available seats
        assert validate_seat_availability(available_seats) is True
        assert validate_seat_availability(available_seats, "Economy") is True
        assert validate_seat_availability(available_seats, "Business") is True

        # Test with no available seats
        assert validate_seat_availability(booked_seats) is False
        assert validate_seat_availability(booked_seats, "Economy") is False
        assert validate_seat_availability(booked_seats, "Business") is False

        # Test with empty list
        assert validate_seat_availability([]) is False

    def test_validate_date_format(self):
        """Test date format validation."""
        # Valid dates
        assert validate_date_format("2023-12-25") is True
        assert validate_date_format("1999-01-01") is True

        # Invalid dates
        assert validate_date_format("25-12-2023") is False  # Wrong format
        assert validate_date_format("2023/12/25") is False  # Wrong separator
        assert validate_date_format("2023-13-01") is False  # Invalid month
        assert validate_date_format("2023-12-32") is False  # Invalid day
        assert validate_date_format("") is False  # Empty

    def test_validate_time_format(self):
        """Test time format validation."""
        # Valid times
        assert validate_time_format("14:30") is True
        assert validate_time_format("00:00") is True
        assert validate_time_format("23:59") is True

        # Invalid times
        assert validate_time_format("1430") is False  # Missing separator
        assert validate_time_format("14:30:00") is False  # Includes seconds
        assert validate_time_format("25:00") is False  # Invalid hour
        assert validate_time_format("14:60") is False  # Invalid minute
        assert validate_time_format("") is False  # Empty

    def test_validate_departure_time(self):
        """Test departure time validation."""
        # Valid departure time (in the future)
        future_time = datetime.now() + timedelta(days=1)
        assert validate_departure_time(future_time) is True

        # Invalid departure time (in the past)
        past_time = datetime.now() - timedelta(days=1)
        assert validate_departure_time(past_time) is False

        # Edge case: exactly now (should be invalid)
        now = datetime.now()
        assert validate_departure_time(now) is False

    def test_validate_positive_number(self):
        """Test positive number validation."""
        # Valid positive numbers
        assert validate_positive_number(1) is True
        assert validate_positive_number(0.1) is True
        assert validate_positive_number(1000) is True

        # Invalid numbers
        assert validate_positive_number(0) is False
        assert validate_positive_number(-1) is False
        assert validate_positive_number(-0.1) is False
        assert validate_positive_number(None) is False

    def test_validate_price(self):
        """Test price validation."""
        # Valid prices for Economy class
        assert validate_price(50.00, "Economy") is True
        assert validate_price(60.00, "Economy") is True

        # Valid prices for Business class
        assert validate_price(100.00, "Business") is True
        assert validate_price(120.00, "Business") is True

        # Invalid prices
        assert validate_price(49.99, "Economy") is False  # Below minimum
        assert validate_price(99.99, "Business") is False  # Below minimum
        assert validate_price(0, "Economy") is False  # Zero
        assert validate_price(-10, "Business") is False  # Negative

    def test_validate_booking_data(self):
        """Test booking data validation."""
        # Valid booking data
        errors = validate_booking_data(
            train_id="T101",
            passenger_name="John Doe",
            seat_class="Economy",
            email="john@example.com",
            phone="+1234567890"
        )
        assert errors == {}

        # Invalid train ID
        errors = validate_booking_data(
            train_id="101",
            passenger_name="John Doe",
            seat_class="Economy"
        )
        assert "train_id" in errors

        # Invalid passenger name
        errors = validate_booking_data(
            train_id="T101",
            passenger_name="A",
            seat_class="Economy"
        )
        assert "passenger_name" in errors

        # Invalid seat class
        errors = validate_booking_data(
            train_id="T101",
            passenger_name="John Doe",
            seat_class="First"
        )
        assert "seat_class" in errors

        # Invalid email
        errors = validate_booking_data(
            train_id="T101",
            passenger_name="John Doe",
            seat_class="Economy",
            email="invalid"
        )
        assert "email" in errors

        # Invalid phone
        errors = validate_booking_data(
            train_id="T101",
            passenger_name="John Doe",
            seat_class="Economy",
            phone="123"
        )
        assert "phone" in errors

    def test_validate_train_data(self):
        """Test train data validation."""
        future_time = datetime.now() + timedelta(days=1)

        # Valid train data
        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=100
        )
        assert errors == {}

        # Invalid train ID
        errors = validate_train_data(
            train_id="101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=100
        )
        assert "train_id" in errors

        # Invalid name
        errors = validate_train_data(
            train_id="T101",
            name="A",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=100
        )
        assert "name" in errors

        # Invalid source
        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="A",
            destination="Boston",
            departure_time=future_time,
            total_seats=100
        )
        assert "source" in errors

        # Invalid destination
        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="B",
            departure_time=future_time,
            total_seats=100
        )
        assert "destination" in errors

        # Same source and destination
        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="New York",
            departure_time=future_time,
            total_seats=100
        )
        assert "route" in errors

        # Past departure time
        past_time = datetime.now() - timedelta(days=1)
        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=past_time,
            total_seats=100
        )
        assert "departure_time" in errors

        # Invalid total seats
        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=0
        )
        assert "total_seats" in errors

        # Too many seats
        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=201  # Assuming max is 200
        )
        assert "total_seats" in errors