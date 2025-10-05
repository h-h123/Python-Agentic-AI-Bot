from src.models import Train, Passenger, Booking
from src.services import (
    add_train,
    book_seat,
    cancel_booking,
    get_train_details,
    get_passenger_bookings
)

def display_menu():
    print("\nRailway Reservation System")
    print("1. Add Train")
    print("2. Book Seat")
    print("3. Cancel Booking")
    print("4. View Train Details")
    print("5. View Passenger Bookings")
    print("6. Exit")

def main():
    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            train_id = input("Enter train ID: ")
            name = input("Enter train name: ")
            total_seats = int(input("Enter total seats: "))
            add_train(train_id, name, total_seats)
            print("Train added successfully!")

        elif choice == "2":
            passenger_id = input("Enter passenger ID: ")
            passenger_name = input("Enter passenger name: ")
            train_id = input("Enter train ID: ")
            seat_number = int(input("Enter seat number: "))
            booking = book_seat(passenger_id, passenger_name, train_id, seat_number)
            if booking:
                print(f"Seat booked successfully! Booking ID: {booking.booking_id}")
            else:
                print("Booking failed. Seat may be unavailable.")

        elif choice == "3":
            booking_id = input("Enter booking ID to cancel: ")
            if cancel_booking(booking_id):
                print("Booking cancelled successfully!")
            else:
                print("Cancellation failed. Invalid booking ID.")

        elif choice == "4":
            train_id = input("Enter train ID: ")
            train = get_train_details(train_id)
            if train:
                print(f"Train ID: {train.train_id}, Name: {train.name}, Total Seats: {train.total_seats}")
                print("Booked Seats:", train.booked_seats)
            else:
                print("Train not found.")

        elif choice == "5":
            passenger_id = input("Enter passenger ID: ")
            bookings = get_passenger_bookings(passenger_id)
            if bookings:
                for booking in bookings:
                    print(f"Booking ID: {booking.booking_id}, Train ID: {booking.train_id}, Seat: {booking.seat_number}")
            else:
                print("No bookings found for this passenger.")

        elif choice == "6":
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()