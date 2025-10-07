import pytest
from datetime import datetime, timedelta
from src.models.train import Train
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.models.payment import Payment, PaymentMethod, PaymentStatus
from src.services.booking_service import BookingService
from src.services.train_service import TrainService
from src.services.payment_service import PaymentService
from src.services.notification_service import NotificationService
from src.utils.exceptions import (
    TrainNotFoundError,
    SeatNotAvailableError,
    BookingNotFoundError,
    PaymentProcessingError
)

class TestPaymentFlow:
    """Integration tests for the complete payment flow in the booking system."""

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
    def notification_service(self):
        """Create and return a NotificationService instance."""
        return NotificationService()

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

    def test_payment_flow_success(self, train_service, booking_service, payment_service, notification_service, sample_train):
        """Test the complete payment flow from booking to payment processing and notification."""
        # 1. Create a booking
        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="John Doe",
            seat_class="Economy",
            email="john@example.com",
            phone="+1234567890"
        )

        # 2. Verify booking was created
        assert booking.booking_id is not None
        assert booking.train == sample_train
        assert booking.passenger.name == "John Doe"
        assert booking.seat.is_booked is True
        assert sample_train.available_seats == 99

        # 3. Verify payment was created and processed
        payments = payment_service.get_payments_by_booking(booking.booking_id)
        assert len(payments) == 1
        payment = payments[0]
        assert payment.booking_id == booking.booking_id
        assert payment.amount == booking.seat.price
        assert payment.status == PaymentStatus.COMPLETED

        # 4. Generate and verify payment receipt
        receipt = payment_service.generate_receipt(payment.payment_id)
        assert "PAYMENT RECEIPT" in receipt
        assert f"Booking ID: {booking.booking_id}" in receipt
        assert f"Amount: {payment.amount}" in receipt

        # 5. Verify notification was sent (mock the email sending)
        with pytest.mock.patch.object(NotificationService, '_send_email', return_value=True):
            email_sent = notification_service.send_booking_confirmation(booking)
            assert email_sent is True

        # 6. Verify SMS notification was sent
        with pytest.mock.patch.object(NotificationService, 'send_sms_notification', return_value=True):
            sms_sent = notification_service.send_booking_confirmation_sms(booking)
            assert sms_sent is True

        # 7. Verify payment receipt notification was sent
        with pytest.mock.patch.object(NotificationService, '_send_email', return_value=True):
            receipt_sent = notification_service.send_payment_receipt(booking, receipt)
            assert receipt_sent is True

    def test_payment_flow_with_cancellation(self, train_service, booking_service, payment_service, notification_service, sample_train):
        """Test the payment flow including booking cancellation and refund processing."""
        # 1. Create a booking
        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Jane Smith",
            seat_class="Business",
            email="jane@example.com",
            phone="+1987654321"
        )

        # 2. Get the associated payment
        payments = payment_service.get_payments_by_booking(booking.booking_id)
        payment = payments[0]
        original_amount = payment.amount

        # 3. Cancel the booking
        booking_details = booking_service.cancel_booking(booking.booking_id)

        # 4. Verify booking was cancelled
        assert booking_details["status"] == "cancelled"
        assert sample_train.available_seats == 100  # Seat should be available again

        # 5. Verify payment was refunded
        refunded_payment = payment_service.get_payment(payment.payment_id)
        assert refunded_payment.status == PaymentStatus.REFUNDED
        assert refunded_payment.refund_amount == (original_amount - booking.cancellation_fee)

        # 6. Verify cancellation notification was sent
        with pytest.mock.patch.object(NotificationService, '_send_email', return_value=True):
            email_sent = notification_service.send_booking_cancellation(booking)
            assert email_sent is True

        # 7. Verify cancellation SMS was sent
        with pytest.mock.patch.object(NotificationService, 'send_sms_notification', return_value=True):
            sms_sent = notification_service.send_cancellation_confirmation_sms(booking)
            assert sms_sent is True

    def test_payment_flow_with_failed_payment(self, train_service, booking_service, payment_service, sample_train):
        """Test the payment flow when payment processing fails."""
        # 1. Create a booking
        booking = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Bob Johnson",
            seat_class="Economy"
        )

        # 2. Get the associated payment
        payments = payment_service.get_payments_by_booking(booking.booking_id)
        payment = payments[0]

        # 3. Simulate payment failure by manually setting status to FAILED
        payment.status = PaymentStatus.FAILED

        # 4. Verify booking still exists but payment failed
        retrieved_booking = booking_service.get_booking(booking.booking_id)
        assert retrieved_booking == booking

        # 5. Verify payment status is FAILED
        failed_payment = payment_service.get_payment(payment.payment_id)
        assert failed_payment.status == PaymentStatus.FAILED

        # 6. Verify seat is still booked (payment failure doesn't cancel booking in this test)
        assert booking.seat.is_booked is True

    def test_payment_flow_with_multiple_bookings(self, train_service, booking_service, payment_service, sample_train):
        """Test the payment flow with multiple bookings for the same passenger."""
        # 1. Create multiple bookings for the same passenger
        booking1 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Alice Brown",
            seat_class="Economy",
            email="alice@example.com"
        )

        booking2 = booking_service.book_seat(
            train_id=sample_train.train_id,
            passenger_name="Alice Brown",
            seat_class="Business",
            email="alice@example.com"
        )

        # 2. Verify both bookings were created
        assert booking1.booking_id is not None
        assert booking2.booking_id is not None
        assert booking1.booking_id != booking2.booking_id

        # 3. Verify payments were created for both bookings
        payments1 = payment_service.get_payments_by_booking(booking1.booking_id)
        payments2 = payment_service.get_payments_by_booking(booking2.booking_id)

        assert len(payments1) == 1
        assert len(payments2) == 1

        payment1 = payments1[0]
        payment2 = payments2[0]

        assert payment1.booking_id == booking1.booking_id
        assert payment2.booking_id == booking2.booking_id
        assert payment1.status == PaymentStatus.COMPLETED
        assert payment2.status == PaymentStatus.COMPLETED

        # 4. Verify seat availability was reduced by 2
        assert sample_train.available_seats == 98

        # 5. Cancel one booking and verify partial refund
        booking_details = booking_service.cancel_booking(booking1.booking_id)

        # 6. Verify first booking was cancelled but second remains
        assert booking_details["status"] == "cancelled"
        with pytest.raises(BookingNotFoundError):
            booking_service.get_booking(booking1.booking_id)

        retrieved_booking2 = booking_service.get_booking(booking2.booking_id)
        assert retrieved_booking2 == booking2

        # 7. Verify first payment was refunded but second remains completed
        refunded_payment = payment_service.get_payment(payment1.payment_id)
        completed_payment = payment_service.get_payment(payment2.payment_id)

        assert refunded_payment.status == PaymentStatus.REFUNDED
        assert completed_payment.status == PaymentStatus.COMPLETED

        # 8. Verify seat availability was increased by 1
        assert sample_train.available_seats == 99