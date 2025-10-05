from booking_controller import BookingController

class CancellationController:
    def __init__(self, booking_controller=None):
        self.booking_controller = booking_controller or BookingController()

    def cancel_booking(self, seat_number):
        """Cancel a booking for the given seat number"""
        passenger_name = self.booking_controller.cancel_booking(seat_number)
        if passenger_name:
            return {
                'success': True,
                'message': f"Booking for {passenger_name} (Seat {seat_number}) cancelled successfully",
                'seat_number': seat_number,
                'passenger_name': passenger_name
            }
        return {
            'success': False,
            'message': "Invalid seat number or seat not booked",
            'seat_number': seat_number
        }

    def verify_seat_before_cancellation(self, seat_number):
        """Check if a seat is currently booked before attempting cancellation"""
        booked_seats = self.booking_controller.get_booked_seats()
        return seat_number in booked_seats