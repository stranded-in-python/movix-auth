import os
from logging import config as logging_config

from fastapi_jwt_auth import AuthJWT
from pydantic import BaseSettings

from core.logger import LOG_LEVEL, get_logging_config


class ModelConfig:
    allow_population_by_field_name = True


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = 'movies'

    # Настройки Redis
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    cache_expiration_in_seconds: int = 300

    # Настройки PSQL
    database_url: str = 'postgresql+asyncpg://yamp_dummy:qweasd123@localhost:5434/yamp_movies_db'

    # Параметры аутентификации
    reset_password_token_secret: str = "SECRET"
    verification_token_secret: str = "SECRET"

    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(__file__))

    log_level: str = LOG_LEVEL


class AuthJWTSettings(BaseSettings):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()


settings = Settings()


# Применяем настройки логирования
logging_config.dictConfig(get_logging_config(level=settings.log_level))
