Here's a complete Python implementation for a railway reservation system with seat booking and cancellation functionality in `main.py`:

```python
class RailwayReservationSystem:
    def __init__(self, total_seats=100):
        self.total_seats = total_seats
        self.available_seats = set(range(1, total_seats + 1))
        self.booked_seats = {}

    def display_available_seats(self):
        print(f"\nAvailable seats: {len(self.available_seats)}/{self.total_seats}")
        print("First 10 available seats:", sorted(self.available_seats)[:10])

    def book_seat(self, passenger_name):
        if not self.available_seats:
            print("No seats available!")
            return None

        seat_number = self.available_seats.pop()
        self.booked_seats[seat_number] = passenger_name
        print(f"Seat {seat_number} booked successfully for {passenger_name}!")
        return seat_number

    def cancel_booking(self, seat_number):
        if seat_number in self.booked_seats:
            passenger_name = self.booked_seats.pop(seat_number)
            self.available_seats.add(seat_number)
            print(f"Booking for seat {seat_number} ({passenger_name}) cancelled successfully!")
            return True
        print(f"No booking found for seat {seat_number}")
        return False

    def show_bookings(self):
        if not self.booked_seats:
            print("No current bookings")
            return

        print("\nCurrent Bookings:")
        for seat, name in sorted(self.booked_seats.items()):
            print(f"Seat {seat}: {name}")

def main():
    system = RailwayReservationSystem()

    while True:
        print("\nRailway Reservation System")
        print("1. Display available seats")
        print("2. Book a seat")
        print("3. Cancel booking")
        print("4. Show all bookings")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            system.display_available_seats()
        elif choice == "2":
            name = input("Enter passenger name: ")
            system.book_seat(name)
        elif choice == "3":
            try:
                seat = int(input("Enter seat number to cancel: "))
                system.cancel_booking(seat)
            except ValueError:
                print("Please enter a valid seat number")
        elif choice == "4":
            system.show_bookings()
        elif choice == "5":
            print("Exiting the system. Thank you!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
```

This implementation includes:

1. A `RailwayReservationSystem` class that manages:
   - Seat availability tracking
   - Booking functionality
   - Cancellation functionality
   - Display of available seats and current bookings

2. A main menu-driven interface with options to:
   - View available seats
   - Book a seat
   - Cancel a booking
   - View all current bookings
   - Exit the system

3. Basic error handling for invalid inputs

The system uses sets for efficient seat management and dictionaries to track bookings. You can run this directly as it contains the `if __name__ == "__main__":` block.