# app/settings.py  – compatible con Pydantic v2.x
from pydantic_settings import BaseSettings, SettingsConfigDict  # 👈 nuevo import

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID:     str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI:  str
    JWT_SECRET:           str = "cambia_est0"
    DATABASE_URL         : str
    OPENAI_API_KEY       : str
    VITE_API_URL         : str
    OSRM_BASE_URL        : str = "http://router.project-osrm.org" # Fallback a demo si no hay local

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

settings = Settings()

GOOGLE_CLIENT_ID     = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI  = settings.GOOGLE_REDIRECT_URI
JWT_SECRET           = settings.JWT_SECRET
OPENAI_API_KEY       = settings.OPENAI_API_KEY
VITE_API_URL         = settings.VITE_API_URL
OSRM_BASE_URL        = settings.OSRM_BASE_URL