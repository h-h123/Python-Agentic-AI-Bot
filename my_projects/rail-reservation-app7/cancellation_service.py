from booking_service import BookingService

class CancellationService:
    def __init__(self, booking_service=None):
        self.booking_service = booking_service or BookingService()

    def process_cancellation(self, seat_number):
        """
        Process a seat cancellation request
        """
        if not isinstance(seat_number, int) or seat_number < 1:
            return {
                'success': False,
                'message': "Invalid seat number provided",
                'seat_number': seat_number
            }

        result = self.booking_service.cancel_booking(seat_number)
        if result['success']:
            return {
                'success': True,
                'message': result['message'],
                'seat_number': seat_number,
                'passenger_name': result['passenger_name'],
                'refund_processed': True
            }
        return result

    def get_cancellation_fee(self, seat_number):
        """
        Calculate cancellation fee (placeholder implementation)
        """
        if self.booking_service.check_seat_availability(seat_number):
            return 0
        return 10  # Fixed fee for demonstration

    def verify_cancellation_eligibility(self, seat_number):
        """
        Verify if a seat is eligible for cancellation
        """
        booked_seats = self.booking_service.get_booking_status()['booked_seats']
        return seat_number in booked_seats