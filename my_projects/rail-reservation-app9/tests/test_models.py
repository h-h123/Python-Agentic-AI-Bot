import pytest
from datetime import datetime
from src.models import Train, Passenger, Booking

def test_train_initialization():
    """Test Train model initialization"""
    train = Train("T101", "Express", 50)
    assert train.train_id == "T101"
    assert train.name == "Express"
    assert train.total_seats == 50
    assert train.booked_seats == set()

def test_train_seat_availability():
    """Test Train seat availability methods"""
    train = Train("T101", "Express", 50)

    # Test available seat
    assert train.is_seat_available(1) is True
    assert train.book_seat(1) is True
    assert train.is_seat_available(1) is False

    # Test unavailable seat
    assert train.is_seat_available(1) is False
    assert train.book_seat(1) is False

    # Test cancel seat
    assert train.cancel_seat(1) is True
    assert train.is_seat_available(1) is True

    # Test invalid seat numbers
    assert train.is_seat_available(0) is False
    assert train.is_seat_available(51) is False
    assert train.book_seat(0) is False
    assert train.book_seat(51) is False

def test_passenger_initialization():
    """Test Passenger model initialization"""
    passenger = Passenger("P101", "John Doe")
    assert passenger.passenger_id == "P101"
    assert passenger.name == "John Doe"
    assert passenger.booking_ids == []

def test_passenger_booking_management():
    """Test Passenger booking management methods"""
    passenger = Passenger("P101", "John Doe")

    # Test adding bookings
    passenger.add_booking("B1000")
    passenger.add_booking("B1001")
    assert passenger.booking_ids == ["B1000", "B1001"]

    # Test removing bookings
    assert passenger.remove_booking("B1000") is True
    assert passenger.booking_ids == ["B1001"]
    assert passenger.remove_booking("B9999") is False

    # Test duplicate booking
    passenger.add_booking("B1000")
    passenger.add_booking("B1000")
    assert passenger.booking_ids == ["B1001", "B1000"]

def test_booking_initialization():
    """Test Booking model initialization"""
    booking = Booking("B1000", "P101", "T101", 1)
    assert booking.booking_id == "B1000"
    assert booking.passenger_id == "P101"
    assert booking.train_id == "T101"
    assert booking.seat_number == 1
    assert booking.is_active is True
    assert isinstance(booking.booking_time, datetime)

def test_booking_cancellation():
    """Test Booking cancellation"""
    booking = Booking("B1000", "P101", "T101", 1)
    assert booking.is_active is True
    booking.cancel()
    assert booking.is_active is False

def test_booking_validation():
    """Test Booking validation methods"""
    booking = Booking("B1000", "P101", "T101", 1)
    assert booking.is_valid() is True
    booking.cancel()
    assert booking.is_valid() is False

def test_booking_details():
    """Test Booking details method"""
    booking = Booking("B1000", "P101", "T101", 1)
    details = booking.get_booking_details()
    assert details["booking_id"] == "B1000"
    assert details["passenger_id"] == "P101"
    assert details["train_id"] == "T101"
    assert details["seat_number"] == 1
    assert details["is_active"] is True
    assert isinstance(details["booking_time"], str)

def test_booking_creation():
    """Test Booking factory method"""
    booking = Booking.create_booking("P101", "T101", 1, "B1000")
    assert booking.booking_id == "B1000"
    assert booking.passenger_id == "P101"
    assert booking.train_id == "T101"
    assert booking.seat_number == 1
    assert booking.is_active is True

def test_train_seat_operations():
    """Test Train seat operations"""
    train = Train("T101", "Express", 50)

    # Book multiple seats
    for seat in [1, 2, 3]:
        assert train.book_seat(seat) is True

    # Try to book already booked seat
    assert train.book_seat(1) is False

    # Cancel a seat
    assert train.cancel_seat(2) is True
    assert train.is_seat_available(2) is True

    # Try to cancel already available seat
    assert train.cancel_seat(2) is False

def test_passenger_booking_operations():
    """Test Passenger booking operations"""
    passenger = Passenger("P101", "John Doe")

    # Add multiple bookings
    passenger.add_booking("B1000")
    passenger.add_booking("B1001")
    passenger.add_booking("B1002")

    # Remove a booking
    assert passenger.remove_booking("B1001") is True
    assert "B1001" not in passenger.booking_ids

    # Try to remove non-existent booking
    assert passenger.remove_booking("B9999") is False

    # Get all bookings
    assert passenger.get_bookings() == ["B1000", "B1002"]

    # Check if passenger has bookings
    assert passenger.has_bookings() is True

    # Clear all bookings
    passenger.remove_booking("B1000")
    passenger.remove_booking("B1002")
    assert passenger.has_bookings() is False