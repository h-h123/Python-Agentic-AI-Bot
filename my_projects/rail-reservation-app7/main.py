class RailwayReservationSystem:
    def __init__(self, total_seats=100):
        self.total_seats = total_seats
        self.available_seats = set(range(1, total_seats + 1))
        self.booked_seats = {}

    def book_seat(self, passenger_name):
        if not self.available_seats:
            return None

        seat_number = self.available_seats.pop()
        self.booked_seats[seat_number] = passenger_name
        return seat_number

    def cancel_booking(self, seat_number):
        if seat_number in self.booked_seats:
            passenger_name = self.booked_seats.pop(seat_number)
            self.available_seats.add(seat_number)
            return passenger_name
        return None

    def get_available_seats(self):
        return len(self.available_seats)

    def get_booked_seats(self):
        return self.booked_seats.copy()

def main():
    system = RailwayReservationSystem()

    while True:
        print("\nRailway Reservation System")
        print("1. Book a seat")
        print("2. Cancel booking")
        print("3. View available seats")
        print("4. View booked seats")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter passenger name: ")
            seat = system.book_seat(name)
            if seat:
                print(f"Seat {seat} booked successfully for {name}!")
            else:
                print("No seats available.")

        elif choice == "2":
            seat = int(input("Enter seat number to cancel: "))
            name = system.cancel_booking(seat)
            if name:
                print(f"Booking for {name} (Seat {seat}) cancelled successfully.")
            else:
                print("Invalid seat number or seat not booked.")

        elif choice == "3":
            print(f"Available seats: {system.get_available_seats()}")

        elif choice == "4":
            booked = system.get_booked_seats()
            if booked:
                print("Booked seats:")
                for seat, name in booked.items():
                    print(f"Seat {seat}: {name}")
            else:
                print("No seats booked yet.")

        elif choice == "5":
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()