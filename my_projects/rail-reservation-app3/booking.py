Since `main.py` already contains a complete implementation of the railway reservation system, I'll create a complementary `booking.py` file that could be used to modularize the booking-related functionality. Here's a clean implementation:

```python
class BookingManager:
    """Handles seat booking and cancellation operations"""

    def __init__(self, total_seats=100):
        self.total_seats = total_seats
        self.available_seats = set(range(1, total_seats + 1))
        self.booked_seats = {}

    def book_seat(self, passenger_name):
        """Book an available seat for a passenger"""
        if not self.available_seats:
            return None, "No seats available!"

        seat_number = self.available_seats.pop()
        self.booked_seats[seat_number] = passenger_name
        return seat_number, f"Seat {seat_number} booked successfully for {passenger_name}!"

    def cancel_booking(self, seat_number):
        """Cancel a booking for a specific seat"""
        if seat_number in self.booked_seats:
            passenger_name = self.booked_seats.pop(seat_number)
            self.available_seats.add(seat_number)
            return True, f"Booking for seat {seat_number} ({passenger_name}) cancelled successfully!"
        return False, f"No booking found for seat {seat_number}"

    def get_booking_info(self, seat_number):
        """Get information about a specific booking"""
        return self.booked_seats.get(seat_number, None)

    def get_all_bookings(self):
        """Get all current bookings"""
        return dict(sorted(self.booked_seats.items()))

    def get_available_seats_count(self):
        """Get count of available seats"""
        return len(self.available_seats)

    def get_first_available_seats(self, count=10):
        """Get first N available seats"""
        return sorted(self.available_seats)[:count]
```

This `booking.py` file:
1. Contains a `BookingManager` class that handles all booking-related operations
2. Provides methods for booking, cancellation, and querying booking information
3. Maintains the same core functionality as in `main.py` but in a more modular way
4. Returns tuples with (status, message) for operations to make it easier to handle in a UI
5. Includes additional helper methods for getting booking information

The main program could then import and use this class while keeping the UI logic separate.