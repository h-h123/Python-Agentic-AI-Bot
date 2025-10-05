import pytest
from src.models import Train, Seat
from src.services import TrainService
from src.exceptions import SeatNotAvailableError, InvalidTrainError
from src.config.constants import (
    SEAT_STATUS_AVAILABLE, SEAT_STATUS_BOOKED, SEAT_STATUS_MAINTENANCE,
    DEFAULT_TRAIN_CAPACITY, MIN_SEAT_NUMBER, MAX_SEAT_NUMBER
)

@pytest.fixture
def train_service():
    service = TrainService()
    return service

@pytest.fixture
def sample_train():
    return Train(
        train_id="T1001",
        name="Express",
        source="New York",
        destination="Boston",
        departure_time="10:00",
        arrival_time="12:00"
    )

def test_add_train_success(train_service, sample_train):
    train_service.add_train(sample_train)
    assert train_service.get_train("T1001") == sample_train

def test_add_duplicate_train(train_service, sample_train):
    train_service.add_train(sample_train)
    with pytest.raises(ValueError):
        train_service.add_train(sample_train)

def test_get_nonexistent_train(train_service):
    assert train_service.get_train("T9999") is None

def test_get_all_trains(train_service, sample_train):
    train_service.add_train(sample_train)
    trains = train_service.get_all_trains()
    assert len(trains) == 1
    assert trains[0] == sample_train

def test_add_seat_success(train_service, sample_train):
    train_service.add_train(sample_train)
    seat = Seat(seat_number=1, status=SEAT_STATUS_AVAILABLE)
    train_service.add_seat("T1001", seat)
    assert train_service.get_seat("T1001", 1) == seat

def test_add_seat_to_nonexistent_train(train_service):
    seat = Seat(seat_number=1, status=SEAT_STATUS_AVAILABLE)
    with pytest.raises(ValueError):
        train_service.add_seat("T9999", seat)

def test_add_duplicate_seat(train_service, sample_train):
    train_service.add_train(sample_train)
    seat1 = Seat(seat_number=1, status=SEAT_STATUS_AVAILABLE)
    seat2 = Seat(seat_number=1, status=SEAT_STATUS_AVAILABLE)
    train_service.add_seat("T1001", seat1)
    with pytest.raises(ValueError):
        train_service.add_seat("T1001", seat2)

def test_get_seat_success(train_service, sample_train):
    train_service.add_train(sample_train)
    seat = Seat(seat_number=1, status=SEAT_STATUS_AVAILABLE)
    train_service.add_seat("T1001", seat)
    assert train_service.get_seat("T1001", 1) == seat

def test_get_nonexistent_seat(train_service, sample_train):
    train_service.add_train(sample_train)
    assert train_service.get_seat("T1001", 99) is None

def test_get_available_seats(train_service, sample_train):
    train_service.add_train(sample_train)
    for i in range(1, 6):
        status = SEAT_STATUS_AVAILABLE if i % 2 == 1 else SEAT_STATUS_BOOKED
        train_service.add_seat("T1001", Seat(seat_number=i, status=status))

    available_seats = train_service.get_available_seats("T1001")
    assert len(available_seats) == 3
    assert all(seat.status == SEAT_STATUS_AVAILABLE for seat in available_seats)

def test_get_booked_seats(train_service, sample_train):
    train_service.add_train(sample_train)
    for i in range(1, 6):
        status = SEAT_STATUS_BOOKED if i % 2 == 1 else SEAT_STATUS_AVAILABLE
        train_service.add_seat("T1001", Seat(seat_number=i, status=status))

    booked_seats = train_service.get_booked_seats("T1001")
    assert len(booked_seats) == 3
    assert all(seat.status == SEAT_STATUS_BOOKED for seat in booked_seats)

def test_update_seat_status(train_service, sample_train):
    train_service.add_train(sample_train)
    seat = Seat(seat_number=1, status=SEAT_STATUS_AVAILABLE)
    train_service.add_seat("T1001", seat)

    train_service.update_seat_status("T1001", 1, SEAT_STATUS_BOOKED)
    updated_seat = train_service.get_seat("T1001", 1)
    assert updated_seat.status == SEAT_STATUS_BOOKED

def test_update_seat_status_invalid(train_service, sample_train):
    train_service.add_train(sample_train)
    seat = Seat(seat_number=1, status=SEAT_STATUS_AVAILABLE)
    train_service.add_seat("T1001", seat)

    with pytest.raises(ValueError):
        train_service.update_seat_status("T1001", 1, "InvalidStatus")

def test_remove_train(train_service, sample_train):
    train_service.add_train(sample_train)
    train_service.remove_train("T1001")
    assert train_service.get_train("T1001") is None

def test_remove_nonexistent_train(train_service):
    with pytest.raises(ValueError):
        train_service.remove_train("T9999")

def test_get_train_occupancy(train_service, sample_train):
    train_service.add_train(sample_train)
    for i in range(1, 6):
        status = SEAT_STATUS_BOOKED if i <= 3 else SEAT_STATUS_AVAILABLE
        train_service.add_seat("T1001", Seat(seat_number=i, status=status))

    occupancy = train_service.get_train_occupancy("T1001")
    assert occupancy == 60.0

def test_get_seat_status(train_service, sample_train):
    train_service.add_train(sample_train)
    seat = Seat(seat_number=1, status=SEAT_STATUS_BOOKED)
    train_service.add_seat("T1001", seat)

    status = train_service.get_seat_status("T1001", 1)
    assert status == SEAT_STATUS_BOOKED

def test_initialize_train_seats(train_service, sample_train):
    train_service.add_train(sample_train)
    train_service.initialize_train_seats("T1001")

    seats = train_service.get_available_seats("T1001")
    assert len(seats) == DEFAULT_TRAIN_CAPACITY
    assert all(seat.status == SEAT_STATUS_AVAILABLE for seat in seats)
    assert all(MIN_SEAT_NUMBER <= seat.seat_number <= MAX_SEAT_NUMBER for seat in seats)