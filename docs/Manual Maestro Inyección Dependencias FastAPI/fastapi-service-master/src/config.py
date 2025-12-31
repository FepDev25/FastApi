from functools import lru_cache
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import Depends

class Settings(BaseSettings):
    APP_NAME: str = "ServiceMaster API"
    VERSION: str = "1.0.0"
    # PostgreSQL Database URL
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG_MODE: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

# Factoría de cache
# lru_cache asegura que solo leamos la configuración una vez
@lru_cache
def get_settings() -> Settings:
    return Settings()

# Poder usar SettingsDep en cualquier lugar sin reescribir la dependencia
SettingsDep = Annotated[Settings, Depends(get_settings)]
