from booking_service import BookingService
from cancellation_service import CancellationService

class TrainService:
    def __init__(self, total_seats=100):
        self.booking_service = BookingService(total_seats)
        self.cancellation_service = CancellationService(self.booking_service)

    def book_seat(self, passenger_name):
        """Book a seat for a passenger"""
        return self.booking_service.book_seat(passenger_name)

    def cancel_booking(self, seat_number):
        """Cancel a booking for a specific seat"""
        return self.cancellation_service.process_cancellation(seat_number)

    def get_booking_status(self):
        """Get current booking status including available and booked seats"""
        return self.booking_service.get_booking_status()

    def check_seat_availability(self, seat_number):
        """Check if a specific seat is available"""
        return self.booking_service.check_seat_availability(seat_number)

    def get_cancellation_fee(self, seat_number):
        """Get cancellation fee for a specific seat"""
        return self.cancellation_service.get_cancellation_fee(seat_number)

    def verify_cancellation_eligibility(self, seat_number):
        """Verify if a seat is eligible for cancellation"""
        return self.cancellation_service.verify_cancellation_eligibility(seat_number)