import pytest
from src.services.train_service import (
    add_train,
    book_seat,
    cancel_booking,
    get_train_details,
    get_passenger_bookings,
    get_available_seats,
    get_train_occupancy
)
from src.config import config
from src.exceptions.custom_exceptions import (
    TrainNotFoundError,
    SeatNotAvailableError,
    BookingNotFoundError,
    PassengerNotFoundError,
    TrainAlreadyExistsError,
    InvalidTrainCapacityError
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
    result = add_train("T101", "Express", 50)
    assert result is True
    assert "T101" in config.trains
    assert config.trains["T101"].name == "Express"
    assert config.trains["T101"].total_seats == 50

def test_add_train_duplicate():
    """Test adding a train with duplicate ID"""
    add_train("T101", "Express", 50)
    with pytest.raises(TrainAlreadyExistsError):
        add_train("T101", "Local", 30)

def test_add_train_invalid_capacity():
    """Test adding a train with invalid capacity"""
    with pytest.raises(InvalidTrainCapacityError):
        add_train("T102", "Express", 0)
    with pytest.raises(InvalidTrainCapacityError):
        add_train("T102", "Express", -10)
    with pytest.raises(InvalidTrainCapacityError):
        add_train("T102", "Express", 101)

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
    with pytest.raises(TrainNotFoundError):
        book_seat("P101", "John Doe", "T999", 1)

def test_book_seat_taken():
    """Test booking an already taken seat"""
    add_train("T101", "Express", 50)
    book_seat("P101", "John Doe", "T101", 1)
    with pytest.raises(SeatNotAvailableError):
        book_seat("P102", "Jane Smith", "T101", 1)

def test_book_seat_invalid_number():
    """Test booking with invalid seat number"""
    add_train("T101", "Express", 50)
    with pytest.raises(SeatNotAvailableError):
        book_seat("P101", "John Doe", "T101", 0)
    with pytest.raises(SeatNotAvailableError):
        book_seat("P101", "John Doe", "T101", 51)

def test_cancel_booking_success():
    """Test cancelling a booking successfully"""
    add_train("T101", "Express", 50)
    booking = book_seat("P101", "John Doe", "T101", 1)
    result = cancel_booking(booking.booking_id)
    assert result is True
    assert booking.is_active is False

def test_cancel_booking_nonexistent():
    """Test cancelling a non-existent booking"""
    with pytest.raises(BookingNotFoundError):
        cancel_booking("B9999")

def test_cancel_booking_already_cancelled():
    """Test cancelling an already cancelled booking"""
    add_train("T101", "Express", 50)
    booking = book_seat("P101", "John Doe", "T101", 1)
    cancel_booking(booking.booking_id)
    with pytest.raises(BookingNotFoundError):
        cancel_booking(booking.booking_id)

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
    with pytest.raises(TrainNotFoundError):
        get_train_details("T999")

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
    with pytest.raises(PassengerNotFoundError):
        get_passenger_bookings("P999")

def test_get_passenger_bookings_cancelled():
    """Test getting passenger bookings with some cancelled"""
    add_train("T101", "Express", 50)
    booking1 = book_seat("P101", "John Doe", "T101", 1)
    booking2 = book_seat("P101", "John Doe", "T101", 2)
    cancel_booking(booking1.booking_id)

    bookings = get_passenger_bookings("P101")
    assert len(bookings) == 1
    assert bookings[0].booking_id == booking2.booking_id

def test_get_available_seats():
    """Test getting available seats for a train"""
    add_train("T101", "Express", 5)
    available = get_available_seats("T101")
    assert available == {1, 2, 3, 4, 5}

    book_seat("P101", "John Doe", "T101", 1)
    available = get_available_seats("T101")
    assert available == {2, 3, 4, 5}

def test_get_available_seats_nonexistent_train():
    """Test getting available seats for a non-existent train"""
    with pytest.raises(TrainNotFoundError):
        get_available_seats("T999")

def test_get_train_occupancy():
    """Test getting train occupancy percentage"""
    add_train("T101", "Express", 10)
    assert get_train_occupancy("T101") == 0.0

    book_seat("P101", "John Doe", "T101", 1)
    assert get_train_occupancy("T101") == 10.0

    book_seat("P102", "Jane Smith", "T101", 2)
    assert get_train_occupancy("T101") == 20.0

def test_get_train_occupancy_nonexistent():
    """Test getting occupancy for a non-existent train"""
    with pytest.raises(TrainNotFoundError):
        get_train_occupancy("T999")

def test_get_train_occupancy_zero_seats():
    """Test getting occupancy for a train with zero seats"""
    with pytest.raises(InvalidTrainCapacityError):
        add_train("T101", "Express", 0)