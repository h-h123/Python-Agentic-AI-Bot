from typing import Dict, Optional, List
from datetime import datetime
import uuid
from src.models.payment import Payment, PaymentStatus, PaymentMethod, PaymentReceipt
from src.models.booking import Booking
from src.config.settings import settings

class PaymentService:
    def __init__(self):
        self.payments: Dict[str, Payment] = {}
        self.receipts: Dict[str, PaymentReceipt] = {}

    def create_payment(self, booking: Booking, payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD,
                      metadata: Optional[dict] = None) -> Payment:
        """Create a new payment record for a booking"""
        if not booking or not isinstance(booking, Booking):
            raise ValueError("Valid booking required")

        payment = Payment(
            payment_id=str(uuid.uuid4()),
            booking_id=booking.booking_id,
            amount=booking.seat.price,
            payment_method=payment_method,
            metadata=metadata or {}
        )

        self.payments[payment.payment_id] = payment
        return payment

    def process_payment(self, payment_id: str) -> bool:
        """Process a payment by its ID"""
        payment = self.payments.get(payment_id)
        if not payment:
            raise ValueError("Payment not found")

        if payment.status != PaymentStatus.PENDING:
            raise ValueError(f"Payment is already {payment.status.name}")

        payment.status = PaymentStatus.COMPLETED
        return True

    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> bool:
        """Process a refund for a payment"""
        payment = self.payments.get(payment_id)
        if not payment:
            raise ValueError("Payment not found")

        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError("Only completed payments can be refunded")

        refund_amount = amount if amount is not None else payment.amount
        if refund_amount > payment.amount:
            raise ValueError("Refund amount cannot exceed original payment amount")

        payment.refund(refund_amount)
        return True

    def get_payment(self, payment_id: str) -> Payment:
        """Get payment details by ID"""
        if payment_id not in self.payments:
            raise ValueError("Payment not found")
        return self.payments[payment_id]

    def get_payments_by_booking(self, booking_id: str) -> List[Payment]:
        """Get all payments for a specific booking"""
        return [p for p in self.payments.values() if p.booking_id == booking_id]

    def generate_receipt(self, payment_id: str) -> str:
        """Generate a payment receipt"""
        payment = self.get_payment(payment_id)
        receipt = PaymentReceipt(payment=payment)
        self.receipts[receipt.receipt_id] = receipt
        return receipt.generate_receipt()

    def get_receipt(self, receipt_id: str) -> PaymentReceipt:
        """Get a payment receipt by ID"""
        if receipt_id not in self.receipts:
            raise ValueError("Receipt not found")
        return self.receipts[receipt_id]

    def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Get the status of a payment"""
        payment = self.get_payment(payment_id)
        return payment.status

    def calculate_cancellation_fee(self, booking: Booking) -> float:
        """Calculate cancellation fee for a booking"""
        if not booking or not isinstance(booking, Booking):
            raise ValueError("Valid booking required")

        return booking.seat.price * (float(settings.cancellation_fee_percentage) / 100)