import sqlite3
from typing import Optional, Dict, List

class DatabaseManager:
    def __init__(self, db_name: str = 'railway_reservation.db'):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS seats (
                    seat_number INTEGER PRIMARY KEY,
                    is_available BOOLEAN DEFAULT 1
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seat_number INTEGER,
                    passenger_name TEXT NOT NULL,
                    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (seat_number) REFERENCES seats(seat_number)
                )
            ''')
            conn.commit()

    def initialize_seats(self, total_seats: int = 100) -> None:
        """Initialize the seats table with available seats"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM seats')
            cursor.executemany(
                'INSERT INTO seats (seat_number, is_available) VALUES (?, 1)',
                [(seat,) for seat in range(1, total_seats + 1)]
            )
            conn.commit()

    def get_available_seats(self) -> List[int]:
        """Get list of available seat numbers"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT seat_number FROM seats WHERE is_available = 1')
            return [row[0] for row in cursor.fetchall()]

    def book_seat(self, passenger_name: str, seat_number: Optional[int] = None) -> bool:
        """Book a seat for a passenger"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            if seat_number is None:
                cursor.execute('SELECT seat_number FROM seats WHERE is_available = 1 LIMIT 1')
                result = cursor.fetchone()
                if not result:
                    return False
                seat_number = result[0]

            cursor.execute('''
                UPDATE seats
                SET is_available = 0
                WHERE seat_number = ? AND is_available = 1
            ''', (seat_number,))

            if cursor.rowcount == 0:
                return False

            cursor.execute('''
                INSERT INTO bookings (seat_number, passenger_name)
                VALUES (?, ?)
            ''', (seat_number, passenger_name))

            conn.commit()
            return True

    def cancel_booking(self, seat_number: int) -> bool:
        """Cancel a booking for a specific seat"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE seats
                SET is_available = 1
                WHERE seat_number = ?
            ''', (seat_number,))

            cursor.execute('''
                DELETE FROM bookings
                WHERE seat_number = ?
            ''', (seat_number,))

            conn.commit()
            return cursor.rowcount > 0

    def get_all_bookings(self) -> Dict[int, str]:
        """Get all current bookings as a dictionary of seat_number: passenger_name"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT seat_number, passenger_name
                FROM bookings
                ORDER BY seat_number
            ''')
            return {row[0]: row[1] for row in cursor.fetchall()}

    def close(self) -> None:
        """Close the database connection"""
        pass  # SQLite connections are automatically closed when going out of scope