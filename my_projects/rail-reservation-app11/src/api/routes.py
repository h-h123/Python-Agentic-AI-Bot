from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from datetime import datetime
from src.models.train import Train, Seat
from src.models.booking import Booking
from src.models.passenger import Passenger
from src.models.payment import Payment, PaymentReceipt
from src.services.booking_service import BookingService
from src.services.train_service import TrainService
from src.services.payment_service import PaymentService
from src.utils.validators import (
    validate_booking_data,
    validate_train_data,
    validate_email,
    validate_phone
)
from src.utils.exceptions import (
    RailwayReservationError,
    TrainNotFoundError,
    SeatNotAvailableError,
    BookingNotFoundError,
    PaymentProcessingError
)
from src.utils.logger import logger, log_booking_event, log_payment_event

router = APIRouter()

@router.get("/", response_model=List[Train])
async def get_all_trains():
    """Get all available trains"""
    train_service = TrainService()
    return train_service.get_all_trains()

@router.get("/{train_id}", response_model=Train)
async def get_train(train_id: str):
    """Get train details by ID"""
    train_service = TrainService()
    train = train_service.get_train(train_id)
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Train with ID {train_id} not found"
        )
    return train

@router.post("/", response_model=Train, status_code=status.HTTP_201_CREATED)
async def create_train(
    train_id: str,
    name: str,
    source: str,
    destination: str,
    departure_time: datetime,
    total_seats: int
):
    """Create a new train"""
    train_service = TrainService()

    # Validate train data
    errors = validate_train_data(train_id, name, source, destination, departure_time, total_seats)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors
        )

    # Create and add the train
    train = Train(
        train_id=train_id,
        name=name,
        source=source,
        destination=destination,
        departure_time=departure_time,
        total_seats=total_seats
    )

    try:
        train_service.add_train(train)
        logger.info(f"Train {train_id} created successfully")
        return train
    except Exception as e:
        logger.error(f"Failed to create train: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create train: {str(e)}"
        )

@router.get("/{train_id}/seats", response_model=List[Seat])
async def get_train_seats(train_id: str):
    """Get all seats for a train"""
    train_service = TrainService()
    train = train_service.get_train(train_id)
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Train with ID {train_id} not found"
        )
    return train.seats

@router.get("/{train_id}/available-seats", response_model=List[Seat])
async def get_available_seats(train_id: str, seat_class: Optional[str] = None):
    """Get available seats for a train, optionally filtered by class"""
    train_service = TrainService()
    try:
        seats = train_service.get_available_seats(train_id, seat_class)
        return seats
    except TrainNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{train_id}/seat-map", response_model=dict)
async def get_seat_map(train_id: str):
    """Get seat map for a train organized by class"""
    train_service = TrainService()
    try:
        seat_map = train_service.get_train_seat_map(train_id)
        return seat_map
    except TrainNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{train_id}/occupancy", response_model=float)
async def get_train_occupancy(train_id: str):
    """Get occupancy percentage for a train"""
    train_service = TrainService()
    try:
        occupancy = train_service.get_train_occupancy(train_id)
        return occupancy
    except TrainNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/search/", response_model=List[Train])
async def search_trains(
    source: Optional[str] = None,
    destination: Optional[str] = None,
    date: Optional[datetime] = None
):
    """Search trains by source, destination, and date"""
    train_service = TrainService()
    try:
        trains = train_service.search_trains(source, destination, date)
        return trains
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{train_id}", response_model=Train)
async def update_train(
    train_id: str,
    name: Optional[str] = None,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    departure_time: Optional[datetime] = None,
    total_seats: Optional[int] = None
):
    """Update train information"""
    train_service = TrainService()
    update_data = {}

    if name:
        update_data['name'] = name
    if source:
        update_data['source'] = source
    if destination:
        update_data['destination'] = destination
    if departure_time:
        update_data['departure_time'] = departure_time
    if total_seats:
        update_data['total_seats'] = total_seats

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )

    try:
        train = train_service.update_train(train_id, **update_data)
        logger.info(f"Train {train_id} updated successfully")
        return train
    except TrainNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{train_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_train(train_id: str):
    """Delete a train"""
    train_service = TrainService()
    try:
        train_service.remove_train(train_id)
        logger.info(f"Train {train_id} deleted successfully")
    except TrainNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{train_id}/seats", response_model=Train)
async def add_seats_to_train(
    train_id: str,
    economy_seats: int = 0,
    business_seats: int = 0
):
    """Add seats to an existing train"""
    if economy_seats <= 0 and business_seats <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify at least one seat to add"
        )

    train_service = TrainService()
    try:
        train = train_service.get_train(train_id)
        if not train:
            raise TrainNotFoundError(train_id)

        # Add new seats
        current_seats = len(train.seats)
        new_seats = []

        if economy_seats > 0:
            start_num = current_seats + 1
            new_seats.extend([
                Seat(f"{i+start_num}", "Economy")
                for i in range(economy_seats)
            ])

        if business_seats > 0:
            start_num = current_seats + economy_seats + 1
            new_seats.extend([
                Seat(f"{i+start_num}", "Business")
                for i in range(business_seats)
            ])

        train.seats.extend(new_seats)
        train.total_seats += (economy_seats + business_seats)
        train.available_seats += (economy_seats + business_seats)

        updated_train = train_service.update_train(
            train_id,
            seats=train.seats,
            total_seats=train.total_seats
        )

        logger.info(f"Added {economy_seats + business_seats} seats to train {train_id}")
        return updated_train

    except TrainNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )