from main import RailwayReservationSystem

class BookingController:
    def __init__(self, total_seats=100):
        self.reservation_system = RailwayReservationSystem(total_seats)

    def book_seat(self, passenger_name):
        return self.reservation_system.book_seat(passenger_name)

    def cancel_booking(self, seat_number):
        return self.reservation_system.cancel_booking(seat_number)

    def get_available_seats_count(self):
        return self.reservation_system.get_available_seats()

    def get_booked_seats(self):
        return self.reservation_system.get_booked_seats()

    def is_seat_available(self, seat_number):
        return seat_number in self.reservation_system.available_seats