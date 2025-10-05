import pytest
from src.models import Train, Seat, Booking
from src.services import BookingService, TrainService
from src.exceptions import SeatNotAvailableError, BookingNotFoundError
from src.config.constants import SEAT_STATUS_AVAILABLE, BOOKING_STATUS_CONFIRMED, BOOKING_STATUS_CANCELLED

@pytest.fixture
def train_service():
    service = TrainService()
    train = Train("T1001", "Express", "New York", "Boston", "10:00", "12:00")
    service.add_train(train)
    for seat_num in range(1, 6):
        service.add_seat("T1001", Seat(seat_num, SEAT_STATUS_AVAILABLE))
    return service

@pytest.fixture
def booking_service(train_service):
    service = BookingService()
    service.set_train_service(train_service)
    return service

def test_book_seat_success(booking_service):
    booking = booking_service.book_seat("T1001", 1, "John Doe")
    assert booking is not None
    assert booking.train_id == "T1001"
    assert booking.seat_number == 1
    assert booking.passenger_name == "John Doe"
    assert booking.status == BOOKING_STATUS_CONFIRMED

def test_book_unavailable_seat(booking_service):
    booking_service.book_seat("T1001", 1, "John Doe")
    with pytest.raises(SeatNotAvailableError):
        booking_service.book_seat("T1001", 1, "Jane Smith")

def test_book_invalid_train(booking_service):
    with pytest.raises(ValueError):
        booking_service.book_seat("T9999", 1, "John Doe")

def test_cancel_booking_success(booking_service):
    booking = booking_service.book_seat("T1001", 1, "John Doe")
    booking_service.cancel_booking(booking.booking_id)
    assert booking_service.get_booking(booking.booking_id).status == BOOKING_STATUS_CANCELLED

def test_cancel_nonexistent_booking(booking_service):
    with pytest.raises(BookingNotFoundError):
        booking_service.cancel_booking("BK-NONE")

def test_get_booking_by_passenger(booking_service):
    booking_service.book_seat("T1001", 1, "John Doe")
    booking_service.book_seat("T1001", 2, "John Doe")
    bookings = booking_service.get_bookings_by_passenger("John Doe")
    assert len(bookings) == 2
    assert all(booking.passenger_name == "John Doe" for booking in bookings)

def test_get_nonexistent_passenger_bookings(booking_service):
    bookings = booking_service.get_bookings_by_passenger("Nonexistent")
    assert len(bookings) == 0

def test_booking_details(booking_service):
    booking = booking_service.book_seat("T1001", 1, "John Doe")
    details = booking_service.get_booking_details(booking.booking_id)
    assert details["booking_id"] == booking.booking_id
    assert details["train_id"] == "T1001"
    assert details["seat_number"] == 1
    assert details["passenger_name"] == "John Doe"
    assert details["status"] == BOOKING_STATUS_CONFIRMED

def test_booking_status(booking_service):
    booking = booking_service.book_seat("T1001", 1, "John Doe")
    status = booking_service.check_booking_status(booking.booking_id)
    assert status == BOOKING_STATUS_CONFIRMED

    booking_service.cancel_booking(booking.booking_id)
    status = booking_service.check_booking_status(booking.booking_id)
    assert status == BOOKING_STATUS_CANCELLED