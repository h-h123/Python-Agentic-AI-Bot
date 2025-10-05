# Railway Reservation System

## Overview
A Python-based railway reservation system that allows users to:
- Book seats on trains
- Cancel existing bookings
- View available seats
- Manage passenger information

## Features
- **Seat Booking**: Reserve seats with passenger details
- **Cancellation**: Cancel bookings and free up seats
- **Availability Check**: View real-time seat availability
- **Database Integration**: SQLite for persistent data storage
- **Configuration Management**: Multiple config formats (INI, JSON)
- **Logging**: Comprehensive logging for debugging

## System Requirements
- Python 3.8+
- SQLite 3+

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/railway-reservation.git
   cd railway-reservation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up configuration:
   - Edit `config.ini` or `config.json` for database settings
   - Default configuration uses SQLite with file `reservations.db`

## Usage

### Running the Application
```bash
python app.py
```

### Command Line Options
```
--config FILE    Specify configuration file (default: config.ini)
--debug          Enable debug logging
--reset          Reset database (WARNING: deletes all data)
```

## Configuration

### Database Settings
Configure in either:
- `config.ini` (INI format)
- `config.json` (JSON format)

Example `config.ini`:
```ini
[database]
type = sqlite
file = reservations.db
timeout = 30

[logging]
level = INFO
file = railway.log
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/book` | POST | Book a new seat |
| `/cancel` | POST | Cancel a booking |
| `/availability` | GET | Check seat availability |
| `/passengers` | GET | List all passengers |

## Data Models

### Passenger
```python
{
    "id": "string",
    "name": "string",
    "age": "integer",
    "seat_number": "string",
    "train_id": "string",
    "booking_time": "datetime"
}
```

### Train
```python
{
    "id": "string",
    "name": "string",
    "source": "string",
    "destination": "string",
    "total_seats": "integer",
    "available_seats": "integer"
}
```

## Example Workflow

1. Check seat availability:
   ```bash
   curl http://localhost:5000/availability?train_id=EXP123
   ```

2. Book a seat:
   ```bash
   curl -X POST http://localhost:5000/book \
     -H "Content-Type: application/json" \
     -d '{"train_id":"EXP123","passenger_name":"John Doe","age":30}'
   ```

3. Cancel a booking:
   ```bash
   curl -X POST http://localhost:5000/cancel \
     -H "Content-Type: application/json" \
     -d '{"booking_id":"ABC123"}'
   ```

## Database Schema

### Tables
1. **trains**
   - id (TEXT PRIMARY KEY)
   - name (TEXT)
   - source (TEXT)
   - destination (TEXT)
   - total_seats (INTEGER)
   - available_seats (INTEGER)

2. **passengers**
   - id (TEXT PRIMARY KEY)
   - name (TEXT)
   - age (INTEGER)
   - seat_number (TEXT)
   - train_id (TEXT)
   - booking_time (DATETIME)
   - FOREIGN KEY(train_id) REFERENCES trains(id)

## Error Handling

The system handles these error cases:
- Double booking attempts
- Invalid train IDs
- Invalid seat numbers
- Database connection issues

## Testing

Run tests with:
```bash
python -m unittest discover tests
```

## Logging

Logs are written to:
- Console (INFO level and above)
- `railway.log` file (configurable)

## License
MIT License - See LICENSE file for details

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Roadmap
- Add payment processing
- Implement user authentication
- Add train schedule management
- Mobile app interface
- Multi-language support