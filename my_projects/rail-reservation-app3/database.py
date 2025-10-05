Here's a `database.py` implementation that would complement your railway reservation system by handling data persistence:

```python
import sqlite3
from typing import Optional, Dict, Set, Tuple

class RailwayDatabase:
    """Handles database operations for the railway reservation system"""

    def __init__(self, db_name: str = 'railway_reservations.db'):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS seats (
                    seat_number INTEGER PRIMARY KEY,
                    is_booked BOOLEAN DEFAULT FALSE,
                    passenger_name TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_info (
                    id INTEGER PRIMARY KEY,
                    total_seats INTEGER
                )
            ''')
            # Initialize system info if not exists
            cursor.execute('SELECT COUNT(*) FROM system_info')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO system_info (id, total_seats) VALUES (1, 100)')
            conn.commit()

    def get_total_seats(self) -> int:
        """Get total number of seats in the system"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT total_seats FROM system_info WHERE id = 1')
            return cursor.fetchone()[0]

    def get_available_seats(self) -> Set[int]:
        """Get all available seat numbers"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT seat_number FROM seats WHERE is_booked = FALSE')
            return {row[0] for row in cursor.fetchall()}

    def get_booked_seats(self) -> Dict[int, str]:
        """Get all booked seats with passenger names"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT seat_number, passenger_name FROM seats WHERE is_booked = TRUE')
            return {row[0]: row[1] for row in cursor.fetchall()}

    def book_seat(self, seat_number: int, passenger_name: str) -> Tuple[bool, str]:
        """Book a specific seat for a passenger"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE seats
                    SET is_booked = TRUE, passenger_name = ?
                    WHERE seat_number = ? AND is_booked = FALSE
                ''', (passenger_name, seat_number))
                if cursor.rowcount == 0:
                    return False, f"Seat {seat_number} is not available for booking"
                conn.commit()
                return True, f"Seat {seat_number} booked successfully for {passenger_name}"
            except sqlite3.Error as e:
                return False, f"Database error: {str(e)}"

    def cancel_booking(self, seat_number: int) -> Tuple[bool, str]:
        """Cancel booking for a specific seat"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE seats
                    SET is_booked = FALSE, passenger_name = NULL
                    WHERE seat_number = ? AND is_booked = TRUE
                ''', (seat_number,))
                if cursor.rowcount == 0:
                    return False, f"No active booking found for seat {seat_number}"
                conn.commit()
                return True, f"Booking for seat {seat_number} cancelled successfully"
            except sqlite3.Error as e:
                return False, f"Database error: {str(e)}"

    def initialize_seats(self, total_seats: int) -> None:
        """Initialize all seats in the database (use with caution)"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                # Clear existing seats
                cursor.execute('DELETE FROM seats')
                # Insert new seats
                cursor.executemany(
                    'INSERT INTO seats (seat_number, is_booked) VALUES (?, FALSE)',
                    [(i,) for i in range(1, total_seats + 1)]
                )
                # Update total seats
                cursor.execute('''
                    UPDATE system_info
                    SET total_seats = ?
                    WHERE id = 1
                ''', (total_seats,))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error initializing seats: {str(e)}")
                conn.rollback()
```

This implementation:

1. Uses SQLite for data persistence
2. Provides methods for all core operations (booking, cancellation, querying)
3. Includes proper type hints
4. Handles database errors gracefully
5. Maintains data integrity with transactions
6. Includes an initialization method for setting up the database
7. Follows the same return pattern (tuple with success status and message) as your other modules

The database schema includes:
- A `seats` table tracking each seat's status and passenger
- A `system_info` table storing system-wide configuration

You can integrate this with your existing system by:
1. Creating a `RailwayDatabase` instance
2. Using its methods instead of the in-memory operations
3. Calling `initialize_seats()` when first setting up the system