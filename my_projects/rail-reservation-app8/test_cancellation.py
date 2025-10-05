import unittest
from booking_system import RailwayReservationSystem

class TestCancellationFunctions(unittest.TestCase):
    def setUp(self):
        """Initialize the railway reservation system with some bookings before each test"""
        self.system = RailwayReservationSystem(total_seats=5)
        # Pre-book some seats for testing cancellations
        self.system.book_seat("Alice", 1)
        self.system.book_seat("Bob", 2)
        self.system.book_seat("Charlie", 3)

    def test_cancel_existing_booking(self):
        """Test cancellation of an existing booking"""
        initial_available = self.system.available_seats
        result = self.system.cancel_booking(2)
        self.assertTrue(result)
        self.assertEqual(self.system.available_seats, initial_available + 1)
        self.assertNotIn(2, self.system.booked_seats)

    def test_cancel_nonexistent_booking(self):
        """Test cancellation of a non-existent booking ID"""
        initial_available = self.system.available_seats
        result = self.system.cancel_booking(99)
        self.assertFalse(result)
        self.assertEqual(self.system.available_seats, initial_available)

    def test_cancel_all_bookings(self):
        """Test cancellation of all existing bookings"""
        # Cancel all pre-booked seats
        for seat_id in [1, 2, 3]:
            result = self.system.cancel_booking(seat_id)
            self.assertTrue(result)

        self.assertEqual(self.system.available_seats, 5)
        self.assertEqual(len(self.system.booked_seats), 0)

    def test_cancel_twice_same_booking(self):
        """Test attempting to cancel the same booking twice"""
        # First cancellation should succeed
        result1 = self.system.cancel_booking(1)
        self.assertTrue(result1)

        # Second cancellation should fail
        result2 = self.system.cancel_booking(1)
        self.assertFalse(result2)

        self.assertEqual(self.system.available_seats, 4)
        self.assertNotIn(1, self.system.booked_seats)

    def test_cancel_booking_with_wrong_id_type(self):
        """Test cancellation with invalid booking ID type"""
        with self.assertRaises(TypeError):
            self.system.cancel_booking("invalid_id")

if __name__ == '__main__':
    unittest.main()