```python
import sqlite3
from typing import Optional, Tuple, Dict, Set

class DatabaseManager:
    def __init__(self, db_name: str = "railway_reservation.db"):
        self.conn = sqlite3.connect(db_name)
        self._create_tables()

    def _create_tables(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seats (
                seat_number INTEGER PRIMARY KEY,
                is_booked BOOLEAN DEFAULT 0,
                passenger_name TEXT
            )
        ''')
        self.conn.commit()

    def initialize_seats(self, total_seats: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM seats")
        cursor.executemany(
            "INSERT INTO seats (seat_number) VALUES (?)",
            [(seat,) for seat in range(1, total_seats + 1)]
        )
        self.conn.commit()

    def book_seat(self, passenger_name: str) -> Tuple[Optional[int], str]:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE seats SET is_booked = 1, passenger_name = ? WHERE is_booked = 0 LIMIT 1",
            (passenger_name,)
        )
        self.conn.commit()

        if cursor.rowcount == 0:
            return None, "No seats available"

        cursor.execute("SELECT seat_number FROM seats WHERE passenger_name = ?", (passenger_name,))
        seat_number = cursor.fetchone()[0]
        return seat_number, f"Seat {seat_number} booked for {passenger_name}"

    def cancel_booking(self, seat_number: int) -> Tuple[bool, str]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT passenger_name FROM seats WHERE seat_number = ? AND is_booked = 1",
            (seat_number,)
        )
        result = cursor.fetchone()

        if not result:
            return False, "Seat not booked or invalid seat number"

        passenger_name = result[0]
        cursor.execute(
            "UPDATE seats SET is_booked = 0, passenger_name = NULL WHERE seat_number = ?",
            (seat_number,)
        )
        self.conn.commit()
        return True, f"Booking for {passenger_name} (Seat {seat_number}) cancelled"

    def get_available_seats(self) -> Set[int]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT seat_number FROM seats WHERE is_booked = 0")
        return {seat[0] for seat in cursor.fetchall()}

    def get_booked_seats(self) -> Dict[int, str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT seat_number, passenger_name FROM seats WHERE is_booked = 1")
        return {seat[0]: seat[1] for seat in cursor.fetchall()}

    def close(self) -> None:
        self.conn.close()
```