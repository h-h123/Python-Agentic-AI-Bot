"""
Integration tests for the Railway Reservation System.

This module contains integration tests that verify the interaction between
different components of the railway reservation system.
"""

from . import (
    test_booking_integration,
    test_train_integration,
    test_payment_integration,
    test_notification_integration
)

__all__ = [
    "test_booking_integration",
    "test_train_integration",
    "test_payment_integration",
    "test_notification_integration"
]