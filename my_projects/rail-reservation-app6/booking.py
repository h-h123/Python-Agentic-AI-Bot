from main import RailwayReservationSystem

class BookingManager:
    def __init__(self, total_seats=100):
        self.reservation_system = RailwayReservationSystem(total_seats)

    def book_seat(self, passenger_name, seat_number=None):
        return self.reservation_system.book_seat(passenger_name, seat_number)

    def cancel_booking(self, seat_number):
        return self.reservation_system.cancel_booking(seat_number)

    def get_available_seats(self):
        return self.reservation_system.available_seats

    def get_booked_seats(self):
        return self.reservation_system.booked_seats

    def display_available_seats(self):
        self.reservation_system.display_available_seats()

    def show_bookings(self):
        self.reservation_system.show_bookings()