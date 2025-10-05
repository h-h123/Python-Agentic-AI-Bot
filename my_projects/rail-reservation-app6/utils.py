import json
from typing import Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

class FileUtils:
    @staticmethod
    def save_data_to_json(file_path: str, data: Union[Dict, List]) -> bool:
        """Save data to a JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    @staticmethod
    def load_data_from_json(file_path: str) -> Optional[Union[Dict, List]]:
        """Load data from a JSON file"""
        try:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

class ValidationUtils:
    @staticmethod
    def validate_seat_number(seat_number: int, total_seats: int) -> bool:
        """Validate if seat number is within valid range"""
        return 1 <= seat_number <= total_seats

    @staticmethod
    def validate_passenger_name(name: str) -> bool:
        """Validate passenger name (non-empty and alphanumeric)"""
        return bool(name.strip()) and name.replace(" ", "").isalnum()

class DateTimeUtils:
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in string format"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_booking_time(timestamp: str) -> str:
        """Format booking timestamp for display"""
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d-%m-%Y %I:%M %p")
        except:
            return timestamp

class DisplayUtils:
    @staticmethod
    def print_seat_matrix(seats: List[int], total_seats: int, seats_per_row: int = 10) -> None:
        """Print seats in a matrix format"""
        print("\nAvailable Seats:")
        for i in range(1, total_seats + 1):
            marker = "X" if i not in seats else str(i).rjust(2)
            print(f"[{marker}]", end=" ")
            if i % seats_per_row == 0:
                print()
        print()