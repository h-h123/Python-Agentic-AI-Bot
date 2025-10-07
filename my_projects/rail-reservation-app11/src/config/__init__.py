from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Railway Reservation System"
    max_seats_per_train: int = 200
    default_seat_classes: list = ["Economy", "Business"]

    class Config:
        env_file = ".env"

settings = Settings()