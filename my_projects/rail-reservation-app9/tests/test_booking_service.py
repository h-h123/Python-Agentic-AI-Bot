import pytest
from datetime import datetime
from src.models import Train, Passenger, Booking
from src.services.booking_service import (
    add_train,
    book_seat,
    cancel_booking,
    get_train_details,
    get_passenger_bookings
)
from src.config import config
from src.exceptions.custom_exceptions import (
    TrainNotFoundError,
    SeatNotAvailableError,
    BookingNotFoundError,
    PassengerNotFoundError
)

@pytest.fixture(autouse=True)
def reset_config():
    """Reset the config before each test"""
    config.trains = {}
    config.passengers = {}
    config.bookings = {}
    config.next_booking_id = 1000

def test_add_train_success():
    """Test adding a new train successfully"""
    assert add_train("T101", "Express", 50) is True
    assert "T101" in config.trains
    assert config.trains["T101"].name == "Express"
    assert config.trains["T101"].total_seats == 50

def test_add_train_duplicate():
    """Test adding a train with duplicate ID"""
    add_train("T101", "Express", 50)
    assert add_train("T101", "Local", 30) is False

def test_add_train_invalid_seats():
    """Test adding a train with invalid seat count"""
    assert add_train("T102", "Express", 0) is False
    assert add_train("T102", "Express", -10) is False

def test_book_seat_success():
    """Test booking a seat successfully"""
    add_train("T101", "Express", 50)
    booking = book_seat("P101", "John Doe", "T101", 1)
    assert booking is not None
    assert booking.booking_id == "B1000"
    assert booking.passenger_id == "P101"
    assert booking.train_id == "T101"
    assert booking.seat_number == 1
    assert booking.is_active is True

def test_book_seat_nonexistent_train():
    """Test booking a seat on a non-existent train"""
    assert book_seat("P101", "John Doe", "T999", 1) is None

def test_book_seat_taken():
    """Test booking an already taken seat"""
    add_train("T101", "Express", 50)
    book_seat("P101", "John Doe", "T101", 1)
    assert book_seat("P102", "Jane Smith", "T101", 1) is None

def test_book_seat_invalid_number():
    """Test booking with invalid seat number"""
    add_train("T101", "Express", 50)
    assert book_seat("P101", "John Doe", "T101", 0) is None
    assert book_seat("P101", "John Doe", "T101", 51) is None

def test_cancel_booking_success():
    """Test cancelling a booking successfully"""
    add_train("T101", "Express", 50)
    booking = book_seat("P101", "John Doe", "T101", 1)
    assert cancel_booking(booking.booking_id) is True
    assert booking.is_active is False

def test_cancel_booking_nonexistent():
    """Test cancelling a non-existent booking"""
    assert cancel_booking("B9999") is False

def test_cancel_booking_already_cancelled():
    """Test cancelling an already cancelled booking"""
    add_train("T101", "Express", 50)
    booking = book_seat("P101", "John Doe", "T101", 1)
    cancel_booking(booking.booking_id)
    assert cancel_booking(booking.booking_id) is False

def test_get_train_details():
    """Test getting train details"""
    add_train("T101", "Express", 50)
    train = get_train_details("T101")
    assert train is not None
    assert train.train_id == "T101"
    assert train.name == "Express"
    assert train.total_seats == 50

def test_get_train_details_nonexistent():
    """Test getting details of a non-existent train"""
    assert get_train_details("T999") is None

def test_get_passenger_bookings():
    """Test getting passenger bookings"""
    add_train("T101", "Express", 50)
    add_train("T102", "Local", 30)
    book_seat("P101", "John Doe", "T101", 1)
    book_seat("P101", "John Doe", "T102", 5)

    bookings = get_passenger_bookings("P101")
    assert len(bookings) == 2
    assert all(b.is_active for b in bookings)

def test_get_passenger_bookings_nonexistent():
    """Test getting bookings for a non-existent passenger"""
    assert get_passenger_bookings("P999") == []

def test_get_passenger_bookings_cancelled():
    """Test getting passenger bookings with some cancelled"""
    add_train("T101", "Express", 50)
    booking1 = book_seat("P101", "John Doe", "T101", 1)
    booking2 = book_seat("P101", "John Doe", "T101", 2)
    cancel_booking(booking1.booking_id)

    bookings = get_passenger_bookings("P101")
    assert len(bookings) == 1
    assert bookings[0].booking_id == booking2.booking_id

def test_train_model():
    """Test Train model functionality"""
    train = Train("T101", "Express", 50)
    assert train.is_seat_available(1) is True
    assert train.book_seat(1) is True
    assert train.is_seat_available(1) is False
    assert train.cancel_seat(1) is True
    assert train.is_seat_available(1) is True

def test_passenger_model():
    """Test Passenger model functionality"""
    passenger = Passenger("P101", "John Doe")
    passenger.add_booking("B1000")
    assert passenger.remove_booking("B1000") is True
    assert passenger.remove_booking("B9999") is False

def test_booking_model():
    """Test Booking model functionality"""
    booking = Booking("B1000", "P101", "T101", 1)
    assert booking.is_valid() is True
    booking.cancel()
    assert booking.is_valid() is False
    assert booking.get_booking_details()["booking_id"] == "B1000"