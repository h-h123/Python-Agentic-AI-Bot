import pytest
from src.models import Passenger
from src.services import PassengerService
from src.exceptions import BookingNotFoundError, InvalidPassengerError
from src.config.constants import MAX_BOOKINGS_PER_PASSENGERS

@pytest.fixture
def passenger_service():
    return PassengerService()

@pytest.fixture
def sample_passenger():
    return Passenger(
        passenger_id="P1001",
        name="John Doe",
        email="john.doe@example.com",
        phone="1234567890"
    )

def test_add_passenger_success(passenger_service):
    passenger = passenger_service.add_passenger(
        passenger_id="P1001",
        name="John Doe",
        email="john.doe@example.com",
        phone="1234567890"
    )
    assert passenger is not None
    assert passenger.passenger_id == "P1001"
    assert passenger.name == "John Doe"
    assert passenger.email == "john.doe@example.com"
    assert passenger.phone == "1234567890"

def test_add_duplicate_passenger(passenger_service):
    passenger_service.add_passenger("P1001", "John Doe")
    with pytest.raises(ValueError):
        passenger_service.add_passenger("P1001", "Jane Doe")

def test_get_passenger_success(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger = passenger_service.get_passenger("P1001")
    assert passenger == sample_passenger

def test_get_nonexistent_passenger(passenger_service):
    assert passenger_service.get_passenger("P9999") is None

def test_get_passenger_by_name_success(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger = passenger_service.get_passenger_by_name("John Doe")
    assert passenger == sample_passenger

def test_get_passenger_by_name_case_insensitive(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger = passenger_service.get_passenger_by_name("john doe")
    assert passenger == sample_passenger

def test_get_passenger_by_name_nonexistent(passenger_service):
    assert passenger_service.get_passenger_by_name("Nonexistent") is None

def test_get_all_passengers(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passengers = passenger_service.get_all_passengers()
    assert len(passengers) == 1
    assert passengers[0] == sample_passenger

def test_update_passenger_contact_success(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger_service.update_passenger_contact(
        "P1001",
        email="new.email@example.com",
        phone="9876543210"
    )
    updated_passenger = passenger_service.get_passenger("P1001")
    assert updated_passenger.email == "new.email@example.com"
    assert updated_passenger.phone == "9876543210"

def test_update_passenger_contact_invalid_email(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    with pytest.raises(ValueError):
        passenger_service.update_passenger_contact(
            "P1001",
            email="invalid-email",
            phone="9876543210"
        )

def test_update_passenger_contact_invalid_phone(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    with pytest.raises(ValueError):
        passenger_service.update_passenger_contact(
            "P1001",
            email="valid@example.com",
            phone="invalid"
        )

def test_update_nonexistent_passenger_contact(passenger_service):
    with pytest.raises(ValueError):
        passenger_service.update_passenger_contact(
            "P9999",
            email="test@example.com"
        )

def test_add_booking_to_passenger_success(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger_service.add_booking_to_passenger("P1001", "BK12345")
    passenger = passenger_service.get_passenger("P1001")
    assert "BK12345" in passenger.bookings
    assert passenger.loyalty_points == 10

def test_add_duplicate_booking_to_passenger(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger_service.add_booking_to_passenger("P1001", "BK12345")
    with pytest.raises(ValueError):
        passenger_service.add_booking_to_passenger("P1001", "BK12345")

def test_add_booking_to_nonexistent_passenger(passenger_service):
    with pytest.raises(ValueError):
        passenger_service.add_booking_to_passenger("P9999", "BK12345")

def test_remove_booking_from_passenger_success(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger_service.add_booking_to_passenger("P1001", "BK12345")
    passenger_service.remove_booking_from_passenger("P1001", "BK12345")
    passenger = passenger_service.get_passenger("P1001")
    assert "BK12345" not in passenger.bookings
    assert passenger.loyalty_points == 0

def test_remove_nonexistent_booking_from_passenger(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    with pytest.raises(ValueError):
        passenger_service.remove_booking_from_passenger("P1001", "BK99999")

def test_remove_booking_from_nonexistent_passenger(passenger_service):
    with pytest.raises(ValueError):
        passenger_service.remove_booking_from_passenger("P9999", "BK12345")

def test_get_passenger_bookings(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger_service.add_booking_to_passenger("P1001", "BK12345")
    passenger_service.add_booking_to_passenger("P1001", "BK67890")
    bookings = passenger_service.get_passenger_bookings("P1001")
    assert len(bookings) == 2
    assert "BK12345" in bookings
    assert "BK67890" in bookings

def test_get_passenger_bookings_nonexistent(passenger_service):
    with pytest.raises(ValueError):
        passenger_service.get_passenger_bookings("P9999")

def test_get_passenger_loyalty_points(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger_service.add_booking_to_passenger("P1001", "BK12345")
    points = passenger_service.get_passenger_loyalty_points("P1001")
    assert points == 10

def test_get_passenger_loyalty_points_nonexistent(passenger_service):
    with pytest.raises(ValueError):
        passenger_service.get_passenger_loyalty_points("P9999")

def test_get_passenger_by_booking_success(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger_service.add_booking_to_passenger("P1001", "BK12345")
    passenger = passenger_service.get_passenger_by_booking("BK12345")
    assert passenger == sample_passenger

def test_get_passenger_by_booking_nonexistent(passenger_service):
    assert passenger_service.get_passenger_by_booking("BK99999") is None

def test_delete_passenger_success(passenger_service, sample_passenger):
    passenger_service.passengers["P1001"] = sample_passenger
    passenger_service.delete_passenger("P1001")
    assert passenger_service.get_passenger("P1001") is None

def test_delete_nonexistent_passenger(passenger_service):
    with pytest.raises(ValueError):
        passenger_service.delete_passenger("P9999")