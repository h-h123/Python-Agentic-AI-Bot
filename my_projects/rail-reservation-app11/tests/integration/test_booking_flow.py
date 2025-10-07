import pytest
from datetime import datetime, timedelta
from src.models.train import Train, Seat
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.services.booking_service import BookingService
from src.services.train_service import TrainService
from src.services.payment_service import PaymentService
from src.utils.exceptions import (
    TrainNotFoundError,
    SeatNotAvailableError,
    BookingNotFoundError,
    PaymentProcessingError
)

class TestBookingFlow:
    """Integration tests for the complete booking flow."""

    @pytest.fixture
    def train_service(self):
        """Create and return a TrainService instance."""
        return TrainService()

    @pytest.fixture
    def booking_service(self):
        """Create and return a BookingService instance."""
        return BookingService()

    @pytest.fixture
    def payment_service(self):
        """Create and return a PaymentService instance."""
        return PaymentService()

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

    def test_complete_booking_flow(self, train_service, booking_service, payment_service, sample_train):
        """Test the complete booking flow from train selection to payment."""
        # 1. Verify train is available
        train = train_service.get_train(sample_train.train_id)
        assert train is not None
        assert train.available_seats == 100

        # 2. Book a seat
        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy",
            email="john@example.com",
            phone="+1234567890"
        )

        assert booking.booking_id is not None
        assert booking.train == sample_train
        assert booking.passenger.name == "John Doe"
        assert booking.seat.seat_class == "Economy"
        assert booking.seat.is_booked is True
        assert sample_train.available_seats == 99

        # 3. Verify booking was created
        retrieved_booking = booking_service.get_booking(booking.booking_id)
        assert retrieved_booking == booking

        # 4. Verify payment was created
        payments = payment_service.get_payments_by_booking(booking.booking_id)
        assert len(payments) == 1
        payment = payments[0]
        assert payment.booking_id == booking.booking_id
        assert payment.amount == booking.seat.price
        assert payment.status.value == "COMPLETED"

        # 5. Generate and verify payment receipt
        receipt = payment_service.generate_receipt(payment.payment_id)
        assert "PAYMENT RECEIPT" in receipt
        assert f"Booking ID: {booking.booking_id}" in receipt
        assert f"Amount: {payment.amount}" in receipt

        # 6. Cancel the booking
        booking_details = booking_service.cancel_booking(booking.booking_id)
        assert booking_details["status"] == "cancelled"
        assert sample_train.available_seats == 100  # Seat should be available again

        # 7. Verify payment was refunded
        refunded_payment = payment_service.get_payment(payment.payment_id)
        assert refunded_payment.status.value == "REFUNDED"
        assert refunded_payment.refund_amount == (payment.amount - booking.cancellation_fee)

        # 8. Verify booking was removed
        with pytest.raises(BookingNotFoundError):
            booking_service.get_booking(booking.booking_id)

    def test_booking_with_multiple_passengers(self, train_service, booking_service, sample_train):
        """Test booking seats for multiple passengers on the same train."""
        # Book seats for 3 different passengers
        booking1 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Alice Smith",
            seat_class="Economy"
        )

        booking2 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Bob Johnson",
            seat_class="Business"
        )

        booking3 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Charlie Brown",
            seat_class="Economy"
        )

        # Verify all bookings exist
        all_bookings = booking_service.get_all_bookings()
        assert len(all_bookings) == 3
        assert booking1 in all_bookings
        assert booking2 in all_bookings
        assert booking3 in all_bookings

        # Verify seat availability was reduced
        assert sample_train.available_seats == 97

        # Verify bookings by train
        train_bookings = booking_service.get_bookings_by_train(sample_train.train_id)
        assert len(train_bookings) == 3

        # Verify bookings by passenger
        alice_bookings = booking_service.get_bookings_by_passenger(booking1.passenger.passenger_id)
        assert len(alice_bookings) == 1
        assert alice_bookings[0] == booking1

    def test_booking_cancellation_flow(self, train_service, booking_service, payment_service, sample_train):
        """Test the complete booking cancellation flow."""
        # Create a booking
        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy"
        )

        # Get the associated payment
        payments = payment_service.get_payments_by_booking(booking.booking_id)
        payment = payments[0]

        # Cancel the booking
        booking_details = booking_service.cancel_booking(booking.booking_id)

        # Verify booking status
        assert booking_details["status"] == "cancelled"

        # Verify seat is available again
        assert sample_train.available_seats == 100

        # Verify payment was refunded
        refunded_payment = payment_service.get_payment(payment.payment_id)
        assert refunded_payment.status.value == "REFUNDED"
        assert refunded_payment.refund_amount == (payment.amount - booking.cancellation_fee)

        # Verify booking was removed
        with pytest.raises(BookingNotFoundError):
            booking_service.get_booking(booking.booking_id)

    def test_booking_with_invalid_data(self, train_service, booking_service, sample_train):
        """Test booking with invalid data handles errors properly."""
        # Test with invalid seat class
        with pytest.raises(InvalidSeatClassError):
            booking_service.book_seat(
                train_id=sample_train.train_id,
                passenger_name="John Doe",
                seat_class="First"
            )

        # Test with non-existent train
        with pytest.raises(TrainNotFoundError):
            booking_service.book_seat(
                train_id="NONEXISTENT",
                passenger_name="John Doe",
                seat_class="Economy"
            )

        # Test cancelling non-existent booking
        with pytest.raises(BookingNotFoundError):
            booking_service.cancel_booking("NONEXISTENT")

    def test_train_occupancy_and_seat_management(self, train_service, booking_service):
        """Test train occupancy and seat management across multiple bookings."""
        # Create a train with 10 seats for easier testing
        departure_time = datetime.now() + timedelta(days=1)
        small_train = Train(
            train_id="T102",
            name="Local",
            source="Chicago",
            destination="Detroit",
            departure_time=departure_time,
            total_seats=10
        )
        train_service.add_train(small_train)

        # Book all seats
        for i in range(10):
            booking_service.book_seat(
                train_id=small_train.train_id,
                passenger_name=f"Passenger {i+1}",
                seat_class="Economy"
            )

        # Verify train is fully booked
        assert small_train.available_seats == 0

        # Try to book one more seat (should fail)
        with pytest.raises(SeatNotAvailableError):
            booking_service.book_seat(
                train_id=small_train.train_id,
                passenger_name="Extra Passenger",
                seat_class="Economy"
            )

        # Cancel one booking
        bookings = booking_service.get_bookings_by_train(small_train.train_id)
        booking_service.cancel_booking(bookings[0].booking_id)

        # Verify one seat is available again
        assert small_train.available_seats == 1

        # Book the available seat
        new_booking = booking_service.book_seat(
            train_id=small_train.train_id,
            passenger_name="New Passenger",
            seat_class="Economy"
        )

        # Verify train is fully booked again
        assert small_train.available_seats == 0

        # Verify the new booking exists
        assert booking_service.get_booking(new_booking.booking_id) == new_booking