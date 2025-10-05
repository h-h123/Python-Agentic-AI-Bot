from typing import Dict, List, Optional
from uuid import uuid4
from datetime import datetime
from src.models import Train, Seat, Booking
from src.exceptions import SeatNotAvailableError, BookingNotFoundError
from src.config.constants import (
    SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED,
    BOOKING_STATUS_CONFIRMED, BOOKING_STATUS_CANCELLED,
    ERROR_MESSAGES
)

class BookingService:
    def __init__(self):
        self.bookings: Dict[str, Booking] = {}
        self.train_service = None

    def set_train_service(self, train_service):
        self.train_service = train_service

    def book_seat(self, train_id: str, seat_number: int, passenger_name: str) -> Booking:
        if not self.train_service:
            raise ValueError("Train service not initialized")

        train = self.train_service.get_train(train_id)
        if not train:
            raise ValueError(ERROR_MESSAGES["invalid_train"])

        seat = train.get_seat(seat_number)
        if not seat or not seat.is_available():
            raise SeatNotAvailableError(ERROR_MESSAGES["seat_not_available"])

        seat.book()
        booking = Booking(
            train_id=train_id,
            seat_number=seat_number,
            passenger_name=passenger_name,
            seat_type=seat.seat_type
        )

        self.bookings[booking.booking_id] = booking
        return booking

    def cancel_booking(self, booking_id: str) -> None:
        if booking_id not in self.bookings:
            raise BookingNotFoundError(ERROR_MESSAGES["booking_not_found"])

        booking = self.bookings[booking_id]
        if booking.status != BOOKING_STATUS_CONFIRMED:
            raise ValueError(ERROR_MESSAGES["booking_not_found"])

        train = self.train_service.get_train(booking.train_id)
        if train:
            seat = train.get_seat(booking.seat_number)
            if seat:
                seat.release()

        booking.cancel()
        self.bookings[booking_id] = booking

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        return self.bookings.get(booking_id)

    def get_bookings_by_passenger(self, passenger_name: str) -> List[Booking]:
        return [booking for booking in self.bookings.values()
                if booking.passenger_name.lower() == passenger_name.lower()
                and booking.status == BOOKING_STATUS_CONFIRMED]

    def get_all_bookings(self) -> List[Booking]:
        return list(self.bookings.values())

    def check_booking_status(self, booking_id: str) -> str:
        booking = self.get_booking(booking_id)
        if not booking:
            raise BookingNotFoundError(ERROR_MESSAGES["booking_not_found"])
        return booking.status

    def get_booking_details(self, booking_id: str) -> dict:
        booking = self.get_booking(booking_id)
        if not booking:
            raise BookingNotFoundError(ERROR_MESSAGES["booking_not_found"])

        return {
            "booking_id": booking.booking_id,
            "train_id": booking.train_id,
            "seat_number": booking.seat_number,
            "passenger_name": booking.passenger_name,
            "booking_time": booking.booking_time,
            "status": booking.status,
            "price": booking.price,
            "seat_type": booking.seat_type
        }