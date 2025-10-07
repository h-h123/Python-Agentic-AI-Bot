import click
from typing import Optional
from datetime import datetime
from src.services import BookingService, TrainService, PaymentService
from src.utils.logger import logger, log_booking_event, log_payment_event
from src.utils.validators import (
    validate_booking_data,
    validate_train_data,
    validate_email,
    validate_phone,
    validate_seat_class
)
from src.utils.exceptions import (
    RailwayReservationError,
    TrainNotFoundError,
    SeatNotAvailableError,
    BookingNotFoundError,
    InvalidSeatClassError,
    PaymentProcessingError,
    ValidationError
)

@click.group()
def cli():
    """Railway Reservation System CLI"""
    pass

@cli.command()
@click.option('--train-id', help="Filter by train ID")
@click.option('--source', help="Filter by source station")
@click.option('--destination', help="Filter by destination station")
@click.option('--date', help="Filter by departure date (YYYY-MM-DD)")
def list_trains(train_id, source, destination, date):
    """List all available trains with optional filters"""
    train_service = TrainService()

    try:
        departure_date = None
        if date:
            departure_date = datetime.strptime(date, "%Y-%m-%d").date()

        trains = train_service.search_trains(source, destination, departure_date)
        if train_id:
            trains = [t for t in trains if t.train_id == train_id]

        if not trains:
            click.echo("No trains found matching your criteria.")
            return

        click.echo("\nAvailable Trains:")
        for train in trains:
            click.echo(f"ID: {train.train_id}")
            click.echo(f"Name: {train.name}")
            click.echo(f"Route: {train.source} → {train.destination}")
            click.echo(f"Departure: {train.departure_time.strftime('%Y-%m-%d %H:%M')}")
            click.echo(f"Available Seats: {train.available_seats}/{train.total_seats}")
            click.echo("-" * 50)

    except ValueError as e:
        click.echo(f"\nError: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"\nUnexpected error: {str(e)}", err=True)

@cli.command()
@click.option('--train-id', required=True, help="ID of the train")
@click.option('--name', required=True, help="Passenger name")
@click.option('--seat-class', required=True, help="Seat class (Economy/Business)")
@click.option('--email', help="Passenger email")
@click.option('--phone', help="Passenger phone number")
def book_seat(train_id, name, seat_class, email, phone):
    """Book a seat on a train"""
    booking_service = BookingService()
    train_service = TrainService()

    try:
        # Validate inputs
        errors = validate_booking_data(train_id, name, seat_class, email, phone)
        if errors:
            for field, message in errors.items():
                click.echo(f"Error: {message}")
            return

        # Check if train exists
        train = train_service.get_train(train_id)
        if not train:
            raise TrainNotFoundError(train_id)

        # Book the seat
        booking = booking_service.book_seat(train_id, name, seat_class, email, phone)

        # Log the booking event
        log_booking_event(
            logger=logger,
            booking_id=booking.booking_id,
            event_type="creation",
            passenger_name=name,
            train_id=train_id,
            seat_number=booking.seat.seat_number,
            seat_class=seat_class
        )

        # Get payment receipt
        receipt = booking_service.get_payment_receipt(booking.booking_id)

        click.echo("\nBooking Successful!")
        click.echo(f"Booking ID: {booking.booking_id}")
        click.echo(f"Train: {train.name} ({train.train_id})")
        click.echo(f"Passenger: {name}")
        click.echo(f"Seat: {booking.seat.seat_number} ({booking.seat.seat_class})")
        click.echo(f"Price: {booking.seat.price} {booking.seat.currency}")
        click.echo("\nPayment Receipt:")
        click.echo(receipt)

    except RailwayReservationError as e:
        click.echo(f"\nError: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"\nUnexpected error: {str(e)}", err=True)

@cli.command()
@click.argument('booking-id')
def cancel_booking(booking_id):
    """Cancel a booking"""
    booking_service = BookingService()

    try:
        # Cancel the booking
        booking_details = booking_service.cancel_booking(booking_id)

        # Log the cancellation event
        log_booking_event(
            logger=logger,
            booking_id=booking_id,
            event_type="cancellation",
            passenger_name=booking_details['passenger_name'],
            train_id=booking_details['train_id'],
            seat_number=booking_details['seat_number'],
            seat_class=booking_details['seat_class'],
            additional_info={
                'cancellation_fee': booking_details['cancellation_fee'],
                'status': booking_details['status']
            }
        )

        click.echo("\nBooking cancelled successfully!")
        click.echo(f"Booking ID: {booking_id}")
        click.echo(f"Cancellation Fee: {booking_details['cancellation_fee']} {booking_details.get('currency', 'USD')}")
        click.echo(f"Refund Amount: {booking_details['price'] - booking_details['cancellation_fee']} {booking_details.get('currency', 'USD')}")

    except BookingNotFoundError as e:
        click.echo(f"\nError: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"\nUnexpected error: {str(e)}", err=True)

@cli.command()
@click.option('--passenger-id', help="Filter by passenger ID")
@click.option('--train-id', help="Filter by train ID")
@click.option('--status', help="Filter by booking status")
def list_bookings(passenger_id, train_id, status):
    """List all current bookings with optional filters"""
    booking_service = BookingService()
    bookings = booking_service.get_all_bookings()

    if passenger_id:
        bookings = [b for b in bookings if b.passenger.passenger_id == passenger_id]
    if train_id:
        bookings = [b for b in bookings if b.train.train_id == train_id]
    if status:
        bookings = [b for b in bookings if b.status.lower() == status.lower()]

    if not bookings:
        click.echo("No bookings found.")
        return

    click.echo("\nCurrent Bookings:")
    for booking in bookings:
        click.echo(f"Booking ID: {booking.booking_id}")
        click.echo(f"Train: {booking.train.name} ({booking.train.train_id})")
        click.echo(f"Passenger: {booking.passenger.name}")
        click.echo(f"Seat: {booking.seat.seat_number} ({booking.seat.seat_class})")
        click.echo(f"Status: {booking.status}")
        click.echo(f"Price: {booking.seat.price} {booking.seat.currency}")
        click.echo("-" * 50)

@cli.command()
@click.argument('train-id')
def view_seat_map(train_id):
    """View seat availability map for a train"""
    train_service = TrainService()

    try:
        seat_map = train_service.get_train_seat_map(train_id)

        click.echo(f"\nSeat Map for Train {train_id}:")
        for seat_class, seats in seat_map.items():
            click.echo(f"\n{seat_class} Class:")
            for seat in seats:
                status = "Booked" if seat['is_booked'] else "Available"
                click.echo(f"  Seat {seat['seat_number']}: {status} (Price: {seat['price']})")

    except TrainNotFoundError as e:
        click.echo(f"\nError: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"\nUnexpected error: {str(e)}", err=True)

@cli.command()
@click.argument('train-id')
@click.option('--economy', type=int, default=0, help="Number of Economy seats to add")
@click.option('--business', type=int, default=0, help="Number of Business seats to add")
def add_train_seats(train_id, economy, business):
    """Add seats to an existing train"""
    train_service = TrainService()

    try:
        if economy <= 0 and business <= 0:
            click.echo("Error: Must specify at least one seat to add", err=True)
            return

        train = train_service.get_train(train_id)
        if not train:
            raise TrainNotFoundError(train_id)

        # Add new seats
        current_seats = len(train.seats)
        new_seats = []

        if economy > 0:
            start_num = current_seats + 1
            new_seats.extend([
                Seat(f"{i+start_num}", "Economy")
                for i in range(economy)
            ])

        if business > 0:
            start_num = current_seats + economy + 1
            new_seats.extend([
                Seat(f"{i+start_num}", "Business")
                for i in range(business)
            ])

        train.seats.extend(new_seats)
        train.total_seats += (economy + business)
        train.available_seats += (economy + business)

        train_service.update_train(train_id, seats=train.seats, total_seats=train.total_seats)

        click.echo(f"\nSuccessfully added {economy + business} seats to train {train_id}")
        click.echo(f"New total seats: {train.total_seats}")
        click.echo(f"New available seats: {train.available_seats}")

    except TrainNotFoundError as e:
        click.echo(f"\nError: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"\nUnexpected error: {str(e)}", err=True)

@cli.command()
@click.argument('booking-id')
def view_booking(booking_id):
    """View detailed information about a booking"""
    booking_service = BookingService()

    try:
        booking = booking_service.get_booking(booking_id)

        click.echo(f"\nBooking Details (ID: {booking.booking_id})")
        click.echo(f"Status: {booking.status}")

        click.echo(f"\nPassenger:")
        click.echo(f"  Name: {booking.passenger.name}")
        if booking.passenger.email:
            click.echo(f"  Email: {booking.passenger.email}")
        if booking.passenger.phone:
            click.echo(f"  Phone: {booking.passenger.phone}")

        click.echo(f"\nTrain:")
        click.echo(f"  ID: {booking.train.train_id}")
        click.echo(f"  Name: {booking.train.name}")
        click.echo(f"  Route: {booking.train.source} → {booking.train.destination}")
        click.echo(f"  Departure: {booking.train.departure_time.strftime('%Y-%m-%d %H:%M')}")

        click.echo(f"\nSeat:")
        click.echo(f"  Number: {booking.seat.seat_number}")
        click.echo(f"  Class: {booking.seat.seat_class}")
        click.echo(f"  Price: {booking.seat.price} {booking.seat.currency}")

        click.echo(f"\nBooking Time: {booking.booking_time.strftime('%Y-%m-%d %H:%M:%S')}")

        if booking.cancellation_fee is not None:
            click.echo(f"Cancellation Fee: {booking.cancellation_fee} {booking.seat.currency}")

    except BookingNotFoundError as e:
        click.echo(f"\nError: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"\nUnexpected error: {str(e)}", err=True)

@cli.command()
@click.option('--train-id', required=True, help="ID of the train")
@click.option('--name', required=True, help="Train name")
@click.option('--source', required=True, help="Source station")
@click.option('--destination', required=True, help="Destination station")
@click.option('--departure', required=True, help="Departure time (YYYY-MM-DD HH:MM)")
@click.option('--total-seats', required=True, type=int, help="Total number of seats")
def add_train(train_id, name, source, destination, departure, total_seats):
    """Add a new train to the system"""
    train_service = TrainService()

    try:
        departure_time = datetime.strptime(departure, "%Y-%m-%d %H:%M")

        # Validate train data
        errors = validate_train_data(train_id, name, source, destination, departure_time, total_seats)
        if errors:
            for field, message in errors.items():
                click.echo(f"Error: {message}")
            return

        # Create and add the train
        from src.models.train import Train
        train = Train(
            train_id=train_id,
            name=name,
            source=source,
            destination=destination,
            departure_time=departure_time,
            total_seats=total_seats
        )

        train_service.add_train(train)

        click.echo(f"\nTrain {train_id} added successfully!")
        click.echo(f"Name: {name}")
        click.echo(f"Route: {source} → {destination}")
        click.echo(f"Departure: {departure_time.strftime('%Y-%m-%d %H:%M')}")
        click.echo(f"Total Seats: {total_seats}")

    except ValueError as e:
        click.echo(f"\nError: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"\nUnexpected error: {str(e)}", err=True)

if __name__ == '__main__':
    cli()