import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'railway_reservation')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# Application settings
MAX_SEATS_PER_TRAIN = 50
BOOKING_PREFIX = 'BK'
TRAIN_PREFIX = 'T'

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'railway_reservation.log')

# API settings (if applicable)
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))