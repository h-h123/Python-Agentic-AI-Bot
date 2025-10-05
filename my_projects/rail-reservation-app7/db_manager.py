import sqlite3
from typing import Dict, Set, Optional, List, Tuple
from booking_repository import BookingRepository
from train_repository import TrainRepository, Train
from seat import Seat

class DatabaseManager:
    def __init__(self, db_name: str = "railway_reservation.db"):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Create tables if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trains (
                    train_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    total_seats INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    departure_time TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seats (
                    seat_number INTEGER,
                    train_id TEXT,
                    is_booked BOOLEAN DEFAULT 0,
                    passenger_name TEXT,
                    coach TEXT,
                    seat_type TEXT DEFAULT 'standard',
                    PRIMARY KEY (seat_number, train_id),
                    FOREIGN KEY (train_id) REFERENCES trains(train_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS passengers (
                    passenger_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    train_id TEXT,
                    seat_number INTEGER,
                    passenger_id TEXT,
                    booking_date TEXT,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (train_id) REFERENCES trains(train_id),
                    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
                    FOREIGN KEY (train_id, seat_number) REFERENCES seats(train_id, seat_number)
                )
            """)

            conn.commit()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

class DatabaseBookingRepository(BookingRepository):
    def __init__(self, train_id: str, db_manager: DatabaseManager):
        self.train_id = train_id
        self.db_manager = db_manager

    def save_booking(self, seat_number: int, passenger_name: str) -> bool:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE seats SET is_booked = 1, passenger_name = ? WHERE seat_number = ? AND train_id = ?",
                (passenger_name, seat_number, self.train_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def remove_booking(self, seat_number: int) -> Optional[str]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT passenger_name FROM seats WHERE seat_number = ? AND train_id = ? AND is_booked = 1",
                (seat_number, self.train_id)
            )
            result = cursor.fetchone()
            if result:
                passenger_name = result[0]
                cursor.execute(
                    "UPDATE seats SET is_booked = 0, passenger_name = NULL WHERE seat_number = ? AND train_id = ?",
                    (seat_number, self.train_id)
                )
                conn.commit()
                return passenger_name
            return None

    def get_all_bookings(self) -> Dict[int, str]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT seat_number, passenger_name FROM seats WHERE train_id = ? AND is_booked = 1",
                (self.train_id,)
            )
            return {row[0]: row[1] for row in cursor.fetchall()}

    def get_available_seats(self) -> Set[int]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT seat_number FROM seats WHERE train_id = ? AND is_booked = 0",
                (self.train_id,)
            )
            return {row[0] for row in cursor.fetchall()}

    def is_seat_available(self, seat_number: int) -> bool:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_booked FROM seats WHERE seat_number = ? AND train_id = ?",
                (seat_number, self.train_id)
            )
            result = cursor.fetchone()
            return result is not None and not result[0]

class DatabaseTrainRepository(TrainRepository):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_train(self, train: Train) -> bool:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO trains VALUES (?, ?, ?, ?, ?, ?)",
                    (train.train_id, train.name, train.total_seats,
                     train.source, train.destination, train.departure_time)
                )

                # Initialize seats for this train
                seats = [(seat, train.train_id) for seat in range(1, train.total_seats + 1)]
                cursor.executemany(
                    "INSERT INTO seats (seat_number, train_id) VALUES (?, ?)",
                    seats
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_train(self, train_id: str) -> Optional[Train]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM trains WHERE train_id = ?",
                (train_id,)
            )
            row = cursor.fetchone()
            if row:
                return Train(*row)
            return None

    def get_all_trains(self) -> List[Train]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trains")
            return [Train(*row) for row in cursor.fetchall()]

    def update_train(self, train_id: str, **kwargs) -> bool:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if not kwargs:
                return False

            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values())
            values.append(train_id)

            cursor.execute(
                f"UPDATE trains SET {set_clause} WHERE train_id = ?",
                values
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_train(self, train_id: str) -> bool:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM seats WHERE train_id = ?", (train_id,))
            cursor.execute("DELETE FROM trains WHERE train_id = ?", (train_id,))
            conn.commit()
            return cursor.rowcount > 0