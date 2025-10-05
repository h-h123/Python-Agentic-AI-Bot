import unittest
from booking_system import RailwayReservationSystem

class TestRailwayReservationSystem(unittest.TestCase):
    def setUp(self):
        """Initialize the railway reservation system before each test"""
        self.system = RailwayReservationSystem(total_seats=10)

    def test_initialization(self):
        """Test if the system initializes correctly with available seats"""
        self.assertEqual(self.system.available_seats, 10)
        self.assertEqual(len(self.system.booked_seats), 0)

    def test_book_seat_success(self):
        """Test successful seat booking"""
        result = self.system.book_seat("Alice", 1)
        self.assertTrue(result)
        self.assertEqual(self.system.available_seats, 9)
        self.assertEqual(len(self.system.booked_seats), 1)

    def test_book_seat_failure(self):
        """Test seat booking when no seats are available"""
        # Book all seats first
        for i in range(10):
            self.system.book_seat(f"User{i}", i+1)

        result = self.system.book_seat("Bob", 11)
        self.assertFalse(result)
        self.assertEqual(self.system.available_seats, 0)

    def test_cancel_booking_success(self):
        """Test successful booking cancellation"""
        self.system.book_seat("Alice", 1)
        result = self.system.cancel_booking(1)
        self.assertTrue(result)
        self.assertEqual(self.system.available_seats, 10)
        self.assertEqual(len(self.system.booked_seats), 0)

    def test_cancel_booking_failure(self):
        """Test cancellation of non-existent booking"""
        result = self.system.cancel_booking(999)
        self.assertFalse(result)
        self.assertEqual(self.system.available_seats, 10)

    def test_duplicate_booking(self):
        """Test booking the same seat twice"""
        self.system.book_seat("Alice", 1)
        result = self.system.book_seat("Bob", 1)
        self.assertFalse(result)
        self.assertEqual(self.system.available_seats, 9)

if __name__ == '__main__':
    unittest.main()