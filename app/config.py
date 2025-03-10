# app/config.py
from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = ""  # JWT uchun maxfiy kalit
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Token muddati (daqiqa)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()