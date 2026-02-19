import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3-pro-preview"
    SCRAPE_HEADLESS: bool = True
    CACHE_TTL_HOURS: int = 12
    REQUEST_TIMEOUT: int = 30
    
    # Tariffs configuration
    TIERS: Dict[str, Dict] = {
        "free": {
            "price": 0,
            "tokens": 30,
            "ig_limit": 12,
            "tg_limit": 20,
            "can_deep_audit": False
        },
        "pro": {
            "price": 20,
            "tokens": 500,
            "ig_limit": 50,
            "tg_limit": 100,
            "can_deep_audit": True
        },
        "ultra": {
            "price": 50,
            "tokens": 2000,
            "ig_limit": 100,
            "tg_limit": 500,
            "can_deep_audit": True
        }
    }

    COST_STANDARD_AUDIT: int = 10
    COST_DEEP_AUDIT: int = 25

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
