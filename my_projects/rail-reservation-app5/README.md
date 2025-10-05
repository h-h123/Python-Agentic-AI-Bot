```markdown
# Railway Reservation System

A Python application for managing railway seat bookings and cancellations.

## Features

- Book available seats for passengers
- Cancel existing bookings
- View available and booked seats
- Data persistence using SQLite database

## Project Structure

```
railway_reservation/
├── main.py          - Main application entry point
├── booking.py       - Core booking system logic
├── database.py      - Database operations
├── utils.py         - Utility functions
└── README.md        - Project documentation
```

## Requirements

- Python 3.8+
- SQLite3 (included in Python standard library)

## Installation

1. Clone the repository
2. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Select options from the menu:
   - Book a seat
   - Cancel booking
   - View available seats
   - View booked seats
   - Exit

## License

MIT
```