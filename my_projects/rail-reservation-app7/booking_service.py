from booking_controller import BookingController
from cancellation_controller import CancellationController

class BookingService:
    def __init__(self, total_seats=100):
        self.booking_controller = BookingController(total_seats)
        self.cancellation_controller = CancellationController(self.booking_controller)

    def book_seat(self, passenger_name):
        """Handle seat booking with validation"""
        if not passenger_name or not passenger_name.strip():
            return {
                'success': False,
                'message': "Passenger name cannot be empty"
            }

        seat_number = self.booking_controller.book_seat(passenger_name)
        if seat_number:
            return {
                'success': True,
                'message': f"Seat {seat_number} booked successfully for {passenger_name}",
                'seat_number': seat_number,
                'passenger_name': passenger_name
            }
        return {
            'success': False,
            'message': "No seats available"
        }

    def cancel_booking(self, seat_number):
        """Handle booking cancellation with validation"""
        if not isinstance(seat_number, int) or seat_number < 1:
            return {
                'success': False,
                'message': "Invalid seat number"
            }

        return self.cancellation_controller.cancel_booking(seat_number)

    def get_booking_status(self):
        """Get current booking status"""
        return {
            'available_seats': self.booking_controller.get_available_seats_count(),
            'booked_seats': self.booking_controller.get_booked_seats()
        }

    def check_seat_availability(self, seat_number):
        """Check if a specific seat is available"""
        if not isinstance(seat_number, int) or seat_number < 1:
            return False
        return self.booking_controller.is_seat_available(seat_number)