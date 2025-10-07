import pytest
from src.utils.validators import (
    validate_email,
    validate_phone,
    validate_passenger_name,
    validate_train_id,
    validate_booking_id,
    validate_seat_class,
    validate_payment_method,
    validate_seat_availability,
    validate_date_format,
    validate_time_format,
    validate_departure_time,
    validate_positive_number,
    validate_price,
    validate_booking_data,
    validate_train_data
)
from src.models.train import Seat
from datetime import datetime, timedelta

class TestValidators:
    """Test cases for all validator functions."""

    def test_validate_email(self):
        """Test email validation."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@sub.domain.co.uk") is True
        assert validate_email("invalid") is False
        assert validate_email("missing@at.com.") is False
        assert validate_email("no@tld") is False

    def test_validate_phone(self):
        """Test phone number validation."""
        assert validate_phone("+1234567890") is True
        assert validate_phone("123-456-7890") is True
        assert validate_phone("(123) 456-7890") is True
        assert validate_phone("12345678") is True
        assert validate_phone("123") is False
        assert validate_phone("abcdefghij") is False
        assert validate_phone("") is False

    def test_validate_passenger_name(self):
        """Test passenger name validation."""
        assert validate_passenger_name("John Doe") is True
        assert validate_passenger_name("Jean-Luc Picard") is True
        assert validate_passenger_name("O'Connor") is True
        assert validate_passenger_name("A") is False
        assert validate_passenger_name("John123") is False
        assert validate_passenger_name("") is False
        assert validate_passenger_name("  ") is False

    def test_validate_train_id(self):
        """Test train ID validation."""
        assert validate_train_id("T101") is True
        assert validate_train_id("EXP202") is True
        assert validate_train_id("A1") is True
        assert validate_train_id("101") is False
        assert validate_train_id("T101A") is False
        assert validate_train_id("T-101") is False
        assert validate_train_id("") is False

    def test_validate_booking_id(self):
        """Test booking ID validation."""
        assert validate_booking_id("123e4567-e89b-12d3-a456-426614174000") is True
        assert validate_booking_id("550e8400-e29b-41d4-a716-446655440000") is True
        assert validate_booking_id("123e4567e89b12d3a456426614174000") is False
        assert validate_booking_id("123e4567-e89b-12d3-a456-42661417400") is False
        assert validate_booking_id("not-a-uuid") is False
        assert validate_booking_id("") is False

    def test_validate_seat_class(self):
        """Test seat class validation."""
        assert validate_seat_class("Economy") is True
        assert validate_seat_class("Business") is True
        assert validate_seat_class("economy") is True
        assert validate_seat_class("First") is False
        assert validate_seat_class("Premium") is False
        assert validate_seat_class("") is False

    def test_validate_payment_method(self):
        """Test payment method validation."""
        assert validate_payment_method("credit_card") is True
        assert validate_payment_method("debit_card") is True
        assert validate_payment_method("paypal") is True
        assert validate_payment_method("bank_transfer") is True
        assert validate_payment_method("mobile_wallet") is True
        assert validate_payment_method("cash") is False
        assert validate_payment_method("check") is False
        assert validate_payment_method("") is False

    def test_validate_seat_availability(self):
        """Test seat availability validation."""
        available_seats = [
            Seat("1A", "Economy", False),
            Seat("2A", "Business", False)
        ]
        booked_seats = [
            Seat("1A", "Economy", True),
            Seat("2A", "Business", True)
        ]

        assert validate_seat_availability(available_seats) is True
        assert validate_seat_availability(available_seats, "Economy") is True
        assert validate_seat_availability(available_seats, "Business") is True
        assert validate_seat_availability(booked_seats) is False
        assert validate_seat_availability(booked_seats, "Economy") is False
        assert validate_seat_availability(booked_seats, "Business") is False
        assert validate_seat_availability([]) is False

    def test_validate_date_format(self):
        """Test date format validation."""
        assert validate_date_format("2023-12-25") is True
        assert validate_date_format("1999-01-01") is True
        assert validate_date_format("25-12-2023") is False
        assert validate_date_format("2023/12/25") is False
        assert validate_date_format("2023-13-01") is False
        assert validate_date_format("2023-12-32") is False
        assert validate_date_format("") is False

    def test_validate_time_format(self):
        """Test time format validation."""
        assert validate_time_format("14:30") is True
        assert validate_time_format("00:00") is True
        assert validate_time_format("23:59") is True
        assert validate_time_format("1430") is False
        assert validate_time_format("14:30:00") is False
        assert validate_time_format("25:00") is False
        assert validate_time_format("14:60") is False
        assert validate_time_format("") is False

    def test_validate_departure_time(self):
        """Test departure time validation."""
        future_time = datetime.now() + timedelta(days=1)
        past_time = datetime.now() - timedelta(days=1)
        now = datetime.now()

        assert validate_departure_time(future_time) is True
        assert validate_departure_time(past_time) is False
        assert validate_departure_time(now) is False

    def test_validate_positive_number(self):
        """Test positive number validation."""
        assert validate_positive_number(1) is True
        assert validate_positive_number(0.1) is True
        assert validate_positive_number(1000) is True
        assert validate_positive_number(0) is False
        assert validate_positive_number(-1) is False
        assert validate_positive_number(-0.1) is False
        assert validate_positive_number(None) is False

    def test_validate_price(self):
        """Test price validation."""
        assert validate_price(50.00, "Economy") is True
        assert validate_price(60.00, "Economy") is True
        assert validate_price(100.00, "Business") is True
        assert validate_price(120.00, "Business") is True
        assert validate_price(49.99, "Economy") is False
        assert validate_price(99.99, "Business") is False
        assert validate_price(0, "Economy") is False
        assert validate_price(-10, "Business") is False

    def test_validate_booking_data(self):
        """Test booking data validation."""
        errors = validate_booking_data(
            train_id="T101",
            passenger_name="John Doe",
            seat_class="Economy",
            email="john@example.com",
            phone="+1234567890"
        )
        assert errors == {}

        errors = validate_booking_data(
            train_id="101",
            passenger_name="John Doe",
            seat_class="Economy"
        )
        assert "train_id" in errors

        errors = validate_booking_data(
            train_id="T101",
            passenger_name="A",
            seat_class="Economy"
        )
        assert "passenger_name" in errors

        errors = validate_booking_data(
            train_id="T101",
            passenger_name="John Doe",
            seat_class="First"
        )
        assert "seat_class" in errors

        errors = validate_booking_data(
            train_id="T101",
            passenger_name="John Doe",
            seat_class="Economy",
            email="invalid"
        )
        assert "email" in errors

        errors = validate_booking_data(
            train_id="T101",
            passenger_name="John Doe",
            seat_class="Economy",
            phone="123"
        )
        assert "phone" in errors

    def test_validate_train_data(self):
        """Test train data validation."""
        future_time = datetime.now() + timedelta(days=1)

        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=100
        )
        assert errors == {}

        errors = validate_train_data(
            train_id="101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=100
        )
        assert "train_id" in errors

        errors = validate_train_data(
            train_id="T101",
            name="A",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=100
        )
        assert "name" in errors

        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="A",
            destination="Boston",
            departure_time=future_time,
            total_seats=100
        )
        assert "source" in errors

        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="B",
            departure_time=future_time,
            total_seats=100
        )
        assert "destination" in errors

        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="New York",
            departure_time=future_time,
            total_seats=100
        )
        assert "route" in errors

        past_time = datetime.now() - timedelta(days=1)
        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=past_time,
            total_seats=100
        )
        assert "departure_time" in errors

        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=0
        )
        assert "total_seats" in errors

        errors = validate_train_data(
            train_id="T101",
            name="Express",
            source="New York",
            destination="Boston",
            departure_time=future_time,
            total_seats=201
        )
        assert "total_seats" in errors