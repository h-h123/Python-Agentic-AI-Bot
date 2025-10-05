from booking import BookingManager

class CancellationManager:
    def __init__(self, booking_manager):
        self.booking_manager = booking_manager

    def cancel_booking(self, seat_number):
        """Cancel a booking for a specific seat number"""
        return self.booking_manager.cancel_booking(seat_number)

    def verify_cancellation(self, seat_number):
        """Verify if a seat is available after cancellation"""
        return seat_number in self.booking_manager.get_available_seats()

    def process_refund(self, seat_number):
        """Simulate refund processing after cancellation"""
        if self.cancel_booking(seat_number):
            print(f"Refund processed for seat {seat_number}")
            return True
        return False