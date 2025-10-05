from src.models import Train, Seat, Booking
from src.services import BookingService, TrainService
from src.exceptions import SeatNotAvailableError, BookingNotFoundError

def display_menu():
    print("\nRailway Reservation System")
    print("1. View Available Trains")
    print("2. View Available Seats")
    print("3. Book a Seat")
    print("4. Cancel Booking")
    print("5. View My Bookings")
    print("6. Exit")

def main():
    train_service = TrainService()
    booking_service = BookingService()

    # Initialize with sample data
    train1 = Train("T1001", "Express", "New York", "Boston", "10:00", "12:00")
    train2 = Train("T1002", "Local", "Boston", "New York", "14:00", "16:00")
    train_service.add_train(train1)
    train_service.add_train(train2)

    for seat_num in range(1, 51):
        train_service.add_seat(train1.train_id, Seat(seat_num, "Available"))
        train_service.add_seat(train2.train_id, Seat(seat_num, "Available"))

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            trains = train_service.get_all_trains()
            for train in trains:
                print(f"Train ID: {train.train_id}, Name: {train.name}, Route: {train.source} to {train.destination}, Time: {train.departure_time} - {train.arrival_time}")

        elif choice == "2":
            train_id = input("Enter Train ID: ")
            seats = train_service.get_available_seats(train_id)
            if seats:
                print(f"Available seats for Train {train_id}: {', '.join(str(seat.seat_number) for seat in seats)}")
            else:
                print("No available seats or invalid Train ID")

        elif choice == "3":
            train_id = input("Enter Train ID: ")
            seat_number = int(input("Enter Seat Number: "))
            passenger_name = input("Enter Passenger Name: ")
            try:
                booking = booking_service.book_seat(train_id, seat_number, passenger_name)
                print(f"Booking successful! Booking ID: {booking.booking_id}")
            except SeatNotAvailableError as e:
                print(f"Error: {e}")

        elif choice == "4":
            booking_id = input("Enter Booking ID to cancel: ")
            try:
                booking_service.cancel_booking(booking_id)
                print("Booking cancelled successfully")
            except BookingNotFoundError as e:
                print(f"Error: {e}")

        elif choice == "5":
            passenger_name = input("Enter Passenger Name: ")
            bookings = booking_service.get_bookings_by_passenger(passenger_name)
            if bookings:
                for booking in bookings:
                    print(f"Booking ID: {booking.booking_id}, Train: {booking.train_id}, Seat: {booking.seat_number}")
            else:
                print("No bookings found")

        elif choice == "6":
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()