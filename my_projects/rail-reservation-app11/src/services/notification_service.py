from typing import Dict, List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.models.booking import Booking
from src.config.settings import settings

class NotificationService:
    def __init__(self):
        self.smtp_server = "smtp.example.com"
        self.smtp_port = 587
        self.smtp_username = "notifications@railway.com"
        self.smtp_password = "securepassword"
        self.sender_email = "notifications@railway.com"
        self.support_email = settings.support_email

    def send_booking_confirmation(self, booking: Booking) -> bool:
        """Send booking confirmation email to passenger"""
        if not booking or not booking.passenger.email:
            return False

        subject = f"Booking Confirmation: {booking.train.name} ({booking.train.train_id})"
        body = f"""
        Dear {booking.passenger.name},

        Your booking has been successfully confirmed!

        Booking Details:
        - Booking ID: {booking.booking_id}
        - Train: {booking.train.name} ({booking.train.train_id})
        - Route: {booking.train.source} to {booking.train.destination}
        - Departure: {booking.train.departure_time.strftime('%Y-%m-%d %H:%M')}
        - Seat: {booking.seat.seat_number} ({booking.seat.seat_class})
        - Price: {booking.seat.price} {settings.currency}

        Thank you for choosing our railway service!

        Best regards,
        Railway Reservation System
        """

        return self._send_email(
            recipient=booking.passenger.email,
            subject=subject,
            body=body
        )

    def send_booking_cancellation(self, booking: Booking) -> bool:
        """Send booking cancellation email to passenger"""
        if not booking or not booking.passenger.email:
            return False

        subject = f"Booking Cancellation: {booking.train.name} ({booking.train.train_id})"
        body = f"""
        Dear {booking.passenger.name},

        Your booking has been successfully cancelled.

        Booking Details:
        - Booking ID: {booking.booking_id}
        - Train: {booking.train.name} ({booking.train.train_id})
        - Route: {booking.train.source} to {booking.train.destination}
        - Departure: {booking.train.departure_time.strftime('%Y-%m-%d %H:%M')}
        - Seat: {booking.seat.seat_number} ({booking.seat.seat_class})

        Cancellation Fee: {booking.cancellation_fee} {settings.currency}

        If you have any questions, please contact our support team.

        Best regards,
        Railway Reservation System
        """

        return self._send_email(
            recipient=booking.passenger.email,
            subject=subject,
            body=body
        )

    def send_payment_receipt(self, booking: Booking, receipt_content: str) -> bool:
        """Send payment receipt email to passenger"""
        if not booking or not booking.passenger.email:
            return False

        subject = f"Payment Receipt: {booking.train.name} ({booking.train.train_id})"
        body = f"""
        Dear {booking.passenger.name},

        Thank you for your payment. Please find your receipt below:

        {receipt_content}

        If you have any questions about your payment, please contact our support team.

        Best regards,
        Railway Reservation System
        """

        return self._send_email(
            recipient=booking.passenger.email,
            subject=subject,
            body=body
        )

    def send_reminder_notification(self, booking: Booking) -> bool:
        """Send departure reminder notification"""
        if not booking or not booking.passenger.email:
            return False

        subject = f"Departure Reminder: {booking.train.name} ({booking.train.train_id})"
        body = f"""
        Dear {booking.passenger.name},

        This is a friendly reminder about your upcoming journey:

        Booking Details:
        - Booking ID: {booking.booking_id}
        - Train: {booking.train.name} ({booking.train.train_id})
        - Route: {booking.train.source} to {booking.train.destination}
        - Departure: {booking.train.departure_time.strftime('%Y-%m-%d %H:%M')}
        - Seat: {booking.seat.seat_number} ({booking.seat.seat_class})

        Please arrive at the station at least 30 minutes before departure.

        Safe travels!

        Best regards,
        Railway Reservation System
        """

        return self._send_email(
            recipient=booking.passenger.email,
            subject=subject,
            body=body
        )

    def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Internal method to send email via SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def send_sms_notification(self, phone_number: str, message: str) -> bool:
        """Simulate sending SMS notification"""
        if not phone_number:
            return False

        print(f"SMS sent to {phone_number}: {message}")
        return True

    def send_booking_confirmation_sms(self, booking: Booking) -> bool:
        """Send booking confirmation via SMS"""
        if not booking or not booking.passenger.phone:
            return False

        message = f"""
        Booking confirmed! ID: {booking.booking_id}
        Train: {booking.train.name}
        {booking.train.source} to {booking.train.destination}
        Seat: {booking.seat.seat_number} ({booking.seat.seat_class})
        Departure: {booking.train.departure_time.strftime('%Y-%m-%d %H:%M')}
        """

        return self.send_sms_notification(booking.passenger.phone, message)

    def send_cancellation_confirmation_sms(self, booking: Booking) -> bool:
        """Send cancellation confirmation via SMS"""
        if not booking or not booking.passenger.phone:
            return False

        message = f"""
        Booking cancelled! ID: {booking.booking_id}
        Train: {booking.train.name}
        Cancellation fee: {booking.cancellation_fee} {settings.currency}
        """

        return self.send_sms_notification(booking.passenger.phone, message)