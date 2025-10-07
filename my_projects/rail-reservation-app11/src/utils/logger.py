import logging
import os
from datetime import datetime
from typing import Optional
from src.config.settings import settings

def setup_logger(name: str = "railway_reservation", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure a logger for the railway reservation system.

    Args:
        name: Name of the logger
        log_file: Optional path to log file. If None, logs to console only.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.logging_level.upper(), logging.INFO))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if log_file is provided
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger

def log_booking_event(
    logger: logging.Logger,
    booking_id: str,
    event_type: str,
    passenger_name: str,
    train_id: str,
    seat_number: str,
    seat_class: str,
    additional_info: Optional[dict] = None
) -> None:
    """
    Log a booking-related event with standardized format.

    Args:
        logger: Logger instance
        booking_id: ID of the booking
        event_type: Type of event (e.g., "creation", "cancellation")
        passenger_name: Name of the passenger
        train_id: ID of the train
        seat_number: Seat number
        seat_class: Seat class
        additional_info: Optional dictionary with additional information
    """
    log_data = {
        "event_type": event_type,
        "booking_id": booking_id,
        "passenger_name": passenger_name,
        "train_id": train_id,
        "seat_number": seat_number,
        "seat_class": seat_class,
        "timestamp": datetime.now().isoformat(),
        **additional_info if additional_info else {}
    }

    logger.info(f"Booking Event: {event_type}", extra=log_data)

def log_payment_event(
    logger: logging.Logger,
    payment_id: str,
    booking_id: str,
    amount: float,
    currency: str,
    status: str,
    payment_method: str,
    additional_info: Optional[dict] = None
) -> None:
    """
    Log a payment-related event with standardized format.

    Args:
        logger: Logger instance
        payment_id: ID of the payment
        booking_id: ID of the associated booking
        amount: Payment amount
        currency: Currency code
        status: Payment status
        payment_method: Payment method used
        additional_info: Optional dictionary with additional information
    """
    log_data = {
        "event_type": "payment",
        "payment_id": payment_id,
        "booking_id": booking_id,
        "amount": amount,
        "currency": currency,
        "status": status,
        "payment_method": payment_method,
        "timestamp": datetime.now().isoformat(),
        **additional_info if additional_info else {}
    }

    logger.info(f"Payment Event: {status}", extra=log_data)

def log_error(
    logger: logging.Logger,
    error_message: str,
    context: Optional[dict] = None,
    exc_info: bool = False
) -> None:
    """
    Log an error with optional context information.

    Args:
        logger: Logger instance
        error_message: Description of the error
        context: Optional dictionary with context information
        exc_info: Whether to include exception information
    """
    log_data = {
        "error": error_message,
        "timestamp": datetime.now().isoformat(),
        **context if context else {}
    }

    logger.error(error_message, extra=log_data, exc_info=exc_info)

def log_system_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    additional_info: Optional[dict] = None
) -> None:
    """
    Log a general system event.

    Args:
        logger: Logger instance
        event_type: Type of system event
        message: Description of the event
        additional_info: Optional dictionary with additional information
    """
    log_data = {
        "event_type": event_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        **additional_info if additional_info else {}
    }

    logger.info(f"System Event: {event_type}", extra=log_data)

# Default logger instance
logger = setup_logger()