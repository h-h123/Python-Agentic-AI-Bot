from typing import List, Dict, Optional
import uuid
from datetime import datetime
from src.models.train import Train, Seat
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.models.payment import Payment, PaymentStatus, PaymentMethod
from src.services.train_service import TrainService

class BookingService:
    def __init__(self):
        self.bookings: Dict[str, Booking] = {}
        self.train_service = TrainService()
        self.payments: Dict[str, Payment] = {}

    def book_seat(self, train_id: str, passenger_name: str, seat_class: str,
                 email: Optional[str] = None, phone: Optional[str] = None) -> Booking:
        train = self.train_service.get_train(train_id)
        if not train:
            raise ValueError("Train not found")

        available_seats = train.get_available_seats_by_class(seat_class)
        if not available_seats:
            raise ValueError(f"No available {seat_class} seats")

        passenger = Passenger(
            passenger_id=str(uuid.uuid4()),
            name=passenger_name,
            email=email,
            phone=phone
        )

        seat = available_seats[0]
        seat.is_booked = True
        train.available_seats -= 1

        booking = Booking(
            booking_id=str(uuid.uuid4()),
            train=train,
            passenger=passenger,
            seat=seat
        )

        self.bookings[booking.booking_id] = booking

        # Create payment record
        payment = Payment(
            payment_id=str(uuid.uuid4()),
            booking_id=booking.booking_id,
            amount=seat.price,
            payment_method=PaymentMethod.CREDIT_CARD
        )
        payment.process_payment()
        self.payments[payment.payment_id] = payment

        return booking

    def cancel_booking(self, booking_id: str) -> dict:
        if booking_id not in self.bookings:
            raise ValueError("Booking not found")

        booking = self.bookings[booking_id]
        booking.cancel()

        # Process refund
        payment = next((p for p in self.payments.values() if p.booking_id == booking_id), None)
        if payment:
            refund_amount = payment.amount - booking.cancellation_fee
            payment.refund(refund_amount)

        del self.bookings[booking_id]
        return booking.get_booking_details()

    def get_booking(self, booking_id: str) -> Booking:
        if booking_id not in self.bookings:
            raise ValueError("Booking not found")
        return self.bookings[booking_id]

    def get_all_bookings(self) -> List[Booking]:
        return list(self.bookings.values())

    def get_bookings_by_passenger(self, passenger_id: str) -> List[Booking]:
        return [booking for booking in self.bookings.values()
                if booking.passenger.passenger_id == passenger_id]

    def get_bookings_by_train(self, train_id: str) -> List[Booking]:
        return [booking for booking in self.bookings.values()
                if booking.train.train_id == train_id]

    def get_payment_receipt(self, booking_id: str) -> str:
        payment = next((p for p in self.payments.values() if p.booking_id == booking_id), None)
        if not payment:
            raise ValueError("Payment not found for this booking")

        receipt = PaymentReceipt(payment=payment)
        return receipt.generate_receipt()