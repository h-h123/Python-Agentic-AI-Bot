from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from src.config.settings import settings

class SeatClass(str, Enum):
    economy = "Economy"
    business = "Business"

class SeatBase(BaseModel):
    seat_number: str
    seat_class: SeatClass
    is_booked: bool = False
    price: float = Field(..., gt=0)

    @validator('seat_class')
    def validate_seat_class(cls, value):
        if value not in [sc.value for sc in SeatClass]:
            raise ValueError(f"Invalid seat class. Must be one of: {[sc.value for sc in SeatClass]}")
        return value

    @validator('price')
    def validate_price(cls, value, values):
        if 'seat_class' in values:
            seat_class = values['seat_class']
            if seat_class == SeatClass.economy and value < float(settings.price_economy):
                raise ValueError(f"Economy seat price must be at least {settings.price_economy}")
            elif seat_class == SeatClass.business and value < float(settings.price_business):
                raise ValueError(f"Business seat price must be at least {settings.price_business}")
        return value

class SeatCreate(SeatBase):
    pass

class SeatResponse(SeatBase):
    class Config:
        orm_mode = True

class TrainBase(BaseModel):
    train_id: str
    name: str
    source: str
    destination: str
    departure_time: datetime
    total_seats: int = Field(..., gt=0, le=settings.max_seats_per_train)

    @validator('departure_time')
    def validate_departure_time(cls, value):
        if value <= datetime.now():
            raise ValueError("Departure time must be in the future")
        return value

    @validator('source', 'destination')
    def validate_locations(cls, value):
        if len(value.strip()) < 2:
            raise ValueError("Location must be at least 2 characters")
        return value.strip()

    @validator('destination')
    def validate_destination_not_same_as_source(cls, value, values):
        if 'source' in values and value.strip().lower() == values['source'].strip().lower():
            raise ValueError("Source and destination cannot be the same")
        return value

class TrainCreate(TrainBase):
    pass

class TrainResponse(TrainBase):
    available_seats: int
    seat_classes: List[str] = settings.default_seat_classes
    seats: List[SeatResponse] = []

    class Config:
        orm_mode = True

class PassengerBase(BaseModel):
    name: str = Field(..., min_length=2)
    email: Optional[str] = None
    phone: Optional[str] = None

    @validator('name')
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        if not all(c.isalpha() or c.isspace() or c in ["-", "'"] for c in value):
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
        return value.strip()

    @validator('email')
    def validate_email(cls, value):
        if value is None:
            return value
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format")
        return value

class PassengerCreate(PassengerBase):
    pass

class PassengerResponse(PassengerBase):
    passenger_id: str
    bookings: List[str] = []

    class Config:
        orm_mode = True

class BookingBase(BaseModel):
    train_id: str
    passenger_name: str
    seat_class: SeatClass

    @validator('passenger_name')
    def validate_passenger_name(cls, value):
        if len(value.strip()) < 2:
            raise ValueError("Passenger name must be at least 2 characters")
        return value.strip()

class BookingCreate(BookingBase):
    email: Optional[str] = None
    phone: Optional[str] = None

class BookingResponse(BookingBase):
    booking_id: str
    passenger: PassengerResponse
    seat: SeatResponse
    booking_time: datetime
    status: str
    cancellation_fee: Optional[float] = None

    class Config:
        orm_mode = True

class PaymentMethod(str, Enum):
    credit_card = "Credit Card"
    debit_card = "Debit Card"
    paypal = "PayPal"
    bank_transfer = "Bank Transfer"
    mobile_wallet = "Mobile Wallet"

class PaymentStatus(str, Enum):
    pending = "Pending"
    completed = "Completed"
    failed = "Failed"
    refunded = "Refunded"

class PaymentBase(BaseModel):
    booking_id: str
    amount: float = Field(..., gt=0)
    currency: str = settings.currency
    payment_method: PaymentMethod

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    payment_id: str
    status: PaymentStatus
    payment_time: datetime
    transaction_reference: str
    refund_amount: Optional[float] = None
    refund_time: Optional[datetime] = None
    metadata: Dict = {}

    class Config:
        orm_mode = True

class PaymentReceiptResponse(BaseModel):
    receipt_id: str
    payment: PaymentResponse
    issued_time: datetime
    receipt_number: str
    content: str

    class Config:
        orm_mode = True

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True

class TrainSearchParams(BaseModel):
    source: Optional[str] = None
    destination: Optional[str] = None
    date: Optional[datetime] = None

class BookingSearchParams(BaseModel):
    passenger_id: Optional[str] = None
    train_id: Optional[str] = None
    status: Optional[str] = None

class SeatMapResponse(BaseModel):
    seat_map: Dict[str, List[Dict[str, str]]]

class OccupancyResponse(BaseModel):
    train_id: str
    total_seats: int
    booked_seats: int
    available_seats: int
    occupancy_percentage: float

class BookingCancellationResponse(BaseModel):
    booking_id: str
    cancellation_fee: float
    refund_amount: float
    status: str
    cancellation_time: datetime

class TrainUpdate(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None
    departure_time: Optional[datetime] = None
    total_seats: Optional[int] = None

class SeatAddition(BaseModel):
    economy_seats: int = Field(default=0, ge=0)
    business_seats: int = Field(default=0, ge=0)

    @validator('economy_seats', 'business_seats')
    def validate_at_least_one_seat(cls, value, values):
        if 'economy_seats' in values and 'business_seats' in values:
            if values['economy_seats'] == 0 and values['business_seats'] == 0:
                raise ValueError("At least one type of seat must be added")
        return value

class SystemInfoResponse(BaseModel):
    app_name: str = settings.app_name
    version: str = "1.0.0"
    max_seats_per_train: int = settings.max_seats_per_train
    default_seat_classes: List[str] = settings.default_seat_classes
    currency: str = settings.currency
    support_email: str = settings.support_email
    environment: str = settings.environment

class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    app_name: str = settings.app_name
    timestamp: datetime = Field(default_factory=datetime.now)