import os
import sqlite3
from datetime import datetime
from src.config.settings import settings

def setup_database():
    """Set up the SQLite database for the railway reservation system."""
    db_path = settings.database_url.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trains (
        train_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        source TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        total_seats INTEGER NOT NULL,
        available_seats INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seats (
        seat_id TEXT PRIMARY KEY,
        train_id TEXT NOT NULL,
        seat_number TEXT NOT NULL,
        seat_class TEXT NOT NULL,
        is_booked BOOLEAN DEFAULT FALSE,
        price REAL NOT NULL,
        FOREIGN KEY (train_id) REFERENCES trains (train_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passengers (
        passenger_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id TEXT PRIMARY KEY,
        passenger_id TEXT NOT NULL,
        train_id TEXT NOT NULL,
        seat_id TEXT NOT NULL,
        booking_time TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'confirmed',
        cancellation_fee REAL,
        FOREIGN KEY (passenger_id) REFERENCES passengers (passenger_id),
        FOREIGN KEY (train_id) REFERENCES trains (train_id),
        FOREIGN KEY (seat_id) REFERENCES seats (seat_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        booking_id TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'USD',
        payment_method TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        payment_time TEXT DEFAULT CURRENT_TIMESTAMP,
        transaction_reference TEXT,
        refund_amount REAL,
        refund_time TEXT,
        metadata TEXT,
        FOREIGN KEY (booking_id) REFERENCES bookings (booking_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receipts (
        receipt_id TEXT PRIMARY KEY,
        payment_id TEXT NOT NULL,
        issued_time TEXT DEFAULT CURRENT_TIMESTAMP,
        receipt_number TEXT NOT NULL,
        FOREIGN KEY (payment_id) REFERENCES payments (payment_id)
    )
    """)

    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trains_source_dest ON trains(source, destination)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trains_departure ON trains(departure_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_seats_train ON seats(train_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_seats_class ON seats(seat_class)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_passenger ON bookings(passenger_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_train ON bookings(train_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_booking ON payments(booking_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)")

    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM trains")
    if cursor.fetchone()[0] == 0:
        # Insert sample trains
        trains = [
            ("T101", "Express", "New York", "Boston", (datetime.now() + timedelta(days=7)).isoformat(), 100, 100),
            ("T102", "Local", "Chicago", "Detroit", (datetime.now() + timedelta(days=3)).isoformat(), 50, 50),
            ("T103", "Regional", "Seattle", "Portland", (datetime.now() + timedelta(days=14)).isoformat(), 75, 75)
        ]
        cursor.executemany("INSERT INTO trains VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", trains)

        # Insert sample seats for each train
        for train_id, _, _, _, _, total_seats, _ in trains:
            economy_seats = int(total_seats * 0.8)
            business_seats = total_seats - economy_seats

            # Economy seats
            for i in range(1, economy_seats + 1):
                seat_id = f"{train_id}-E-{i}"
                cursor.execute("""
                INSERT INTO seats VALUES (?, ?, ?, ?, ?, ?)
                """, (seat_id, train_id, f"{i}", "Economy", False, 50.00))

            # Business seats
            for i in range(1, business_seats + 1):
                seat_id = f"{train_id}-B-{i}"
                cursor.execute("""
                INSERT INTO seats VALUES (?, ?, ?, ?, ?, ?)
                """, (seat_id, train_id, f"{i}", "Business", False, 100.00))

    conn.commit()
    conn.close()
    print(f"Database setup complete at {db_path}")

if __name__ == "__main__":
    setup_database()