import os
from logging import config as logging_config

from pydantic import SecretStr
from pydantic.env_settings import BaseSettings

from core.logger import LOG_LEVEL, get_logging_config


class ModelConfig:
    allow_population_by_field_name = True


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = 'movies'

    # Настройки Redis
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cache_expiration_in_seconds: int = 300

    # Настройки PSQL
    pghost: str = "localhost"
    pgport: str = "5434"
    pgdb: str = "yamp_movies_db"
    pguser: str = "yamp_dummy"
    pgpassword: str = "qweasd123"
    database_adapter: str = "postgresql"
    database_sqlalchemy_adapter: str = "postgresql+asyncpg"
    # Параметры аутентификации
    reset_password_token_secret: SecretStr
    verification_password_token_secret: SecretStr
    access_token_secret: SecretStr
    refresh_token_secret: SecretStr

    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(__file__))

    log_level: str = LOG_LEVEL


settings = Settings()  # type: ignore


def get_database_url() -> str:
    return (
        f"{settings.database_adapter}://{settings.pguser}:"
        f"{settings.pgpassword}@{settings.pghost}:{settings.pgport}/{settings.pgdb}"
    )


def get_database_url_async() -> str:
    return (
        f"{settings.database_sqlalchemy_adapter}://{settings.pguser}:"
        f"{settings.pgpassword}@{settings.pghost}:{settings.pgport}/{settings.pgdb}"
    )


# Применяем настройки логирования
logging_config.dictConfig(get_logging_config(level=settings.log_level))
