from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
import uuid
from enum import Enum, auto

class PaymentStatus(Enum):
    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()
    REFUNDED = auto()

class PaymentMethod(Enum):
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    PAYPAL = "PayPal"
    BANK_TRANSFER = "Bank Transfer"
    MOBILE_WALLET = "Mobile Wallet"

@dataclass
class Payment:
    payment_id: str
    booking_id: str
    amount: float
    currency: str = "USD"
    payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD
    status: PaymentStatus = PaymentStatus.PENDING
    payment_time: datetime = field(default_factory=datetime.now)
    transaction_reference: Optional[str] = None
    refund_amount: Optional[float] = None
    refund_time: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.payment_id:
            self.payment_id = str(uuid.uuid4())

        if not self.transaction_reference:
            self.transaction_reference = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        from src.config.settings import settings
        if not self.currency:
            self.currency = settings.currency

    def process_payment(self) -> bool:
        """Simulate payment processing"""
        self.status = PaymentStatus.COMPLETED
        return True

    def refund(self, amount: Optional[float] = None) -> bool:
        """Process refund for the payment"""
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Only completed payments can be refunded")

        refund_amount = amount if amount is not None else self.amount
        if refund_amount > self.amount:
            raise ValueError("Refund amount cannot exceed original payment amount")

        self.status = PaymentStatus.REFUNDED
        self.refund_amount = refund_amount
        self.refund_time = datetime.now()
        return True

    def get_payment_details(self) -> Dict:
        """Return payment details as dictionary"""
        return {
            "payment_id": self.payment_id,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "currency": self.currency,
            "payment_method": self.payment_method.value,
            "status": self.status.name,
            "payment_time": self.payment_time.isoformat(),
            "transaction_reference": self.transaction_reference,
            "refund_amount": self.refund_amount,
            "refund_time": self.refund_time.isoformat() if self.refund_time else None,
            "metadata": self.metadata
        }

@dataclass
class PaymentReceipt:
    receipt_id: str
    payment: Payment
    issued_time: datetime = field(default_factory=datetime.now)
    receipt_number: str = ""

    def __post_init__(self):
        if not self.receipt_id:
            self.receipt_id = str(uuid.uuid4())
        if not self.receipt_number:
            self.receipt_number = f"RCPT-{uuid.uuid4().hex[:10].upper()}"

    def generate_receipt(self) -> str:
        """Generate a formatted receipt string"""
        payment_details = self.payment.get_payment_details()
        return (
            f"=== PAYMENT RECEIPT ===\n"
            f"Receipt Number: {self.receipt_number}\n"
            f"Date: {self.issued_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"\n"
            f"Payment ID: {payment_details['payment_id']}\n"
            f"Booking ID: {payment_details['booking_id']}\n"
            f"Amount: {payment_details['amount']} {payment_details['currency']}\n"
            f"Payment Method: {payment_details['payment_method']}\n"
            f"Status: {payment_details['status']}\n"
            f"Transaction Ref: {payment_details['transaction_reference']}\n"
            f"\n"
            f"=== END RECEIPT ==="
        )