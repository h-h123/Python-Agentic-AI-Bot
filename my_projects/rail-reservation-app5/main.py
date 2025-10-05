```python
class RailwayReservationSystem:
    def __init__(self, total_seats=100):
        self.total_seats = total_seats
        self.available_seats = set(range(1, total_seats + 1))
        self.booked_seats = {}

    def book_seat(self, passenger_name):
        if not self.available_seats:
            return None, "No seats available"

        seat_number = self.available_seats.pop()
        self.booked_seats[seat_number] = passenger_name
        return seat_number, f"Seat {seat_number} booked for {passenger_name}"

    def cancel_booking(self, seat_number):
        if seat_number not in self.booked_seats:
            return False, "Seat not booked or invalid seat number"

        passenger_name = self.booked_seats.pop(seat_number)
        self.available_seats.add(seat_number)
        return True, f"Booking for {passenger_name} (Seat {seat_number}) cancelled"

    def display_available_seats(self):
        return sorted(self.available_seats)

    def display_booked_seats(self):
        return self.booked_seats

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
            seat, message = system.book_seat(name)
            print(message)
        elif choice == "2":
            seat = int(input("Enter seat number to cancel: "))
            success, message = system.cancel_booking(seat)
            print(message)
        elif choice == "3":
            print("Available seats:", system.display_available_seats())
        elif choice == "4":
            print("Booked seats:", system.display_booked_seats())
        elif choice == "5":
            print("Exiting system...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
```