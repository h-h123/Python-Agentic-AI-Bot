class RailwayReservationSystem:
    def __init__(self, total_seats=100):
        self.total_seats = total_seats
        self.available_seats = list(range(1, total_seats + 1))
        self.booked_seats = {}

    def display_available_seats(self):
        print(f"Available seats: {len(self.available_seats)}/{self.total_seats}")
        print(f"Seat numbers: {self.available_seats}")

    def book_seat(self, passenger_name, seat_number=None):
        if not self.available_seats:
            print("No seats available for booking.")
            return False

        if seat_number is None:
            seat_number = self.available_seats[0]
        elif seat_number not in self.available_seats:
            print(f"Seat {seat_number} is not available.")
            return False

        self.available_seats.remove(seat_number)
        self.booked_seats[seat_number] = passenger_name
        print(f"Seat {seat_number} booked successfully for {passenger_name}.")
        return True

    def cancel_booking(self, seat_number):
        if seat_number not in self.booked_seats:
            print(f"No booking found for seat {seat_number}.")
            return False

        passenger_name = self.booked_seats.pop(seat_number)
        self.available_seats.append(seat_number)
        self.available_seats.sort()
        print(f"Booking for seat {seat_number} (Passenger: {passenger_name}) cancelled successfully.")
        return True

    def show_bookings(self):
        if not self.booked_seats:
            print("No bookings found.")
            return

        print("Current Bookings:")
        for seat, passenger in sorted(self.booked_seats.items()):
            print(f"Seat {seat}: {passenger}")

def main():
    system = RailwayReservationSystem()

    while True:
        print("\nRailway Reservation System")
        print("1. Display Available Seats")
        print("2. Book a Seat")
        print("3. Cancel Booking")
        print("4. Show All Bookings")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            system.display_available_seats()
        elif choice == "2":
            name = input("Enter passenger name: ")
            seat_input = input("Enter seat number (leave empty for auto-assign): ")
            seat_number = int(seat_input) if seat_input else None
            system.book_seat(name, seat_number)
        elif choice == "3":
            seat_number = int(input("Enter seat number to cancel: "))
            system.cancel_booking(seat_number)
        elif choice == "4":
            system.show_bookings()
        elif choice == "5":
            print("Exiting the system. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()