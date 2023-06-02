import os
from logging import config as logging_config

from pydantic import BaseSettings, SecretStr

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
    pghost: str = "localhost"
    pgport: str = "5434"
    pgdb: str = "yamp_movies_db"
    pguser: str = "yamp_dummy"
    pgpassword: str = "qweasd123"
    database_adapter: str = "postgresql"
    database_sqlalchemy_adapter: str = "postgresql+asyncpg"
    database_url: str = (
        f"{database_adapter}:" f"//{pguser}:{pgpassword}" f"@{pghost}:{pgport}/{pgdb}"
    )
    database_url_async: str = (
        f"{database_sqlalchemy_adapter}:"
        f"//{pguser}:{pgpassword}"
        f"@{pghost}:{pgport}/{pgdb}"
    )
    # DATABASE_URL: str = 'postgresql+asyncpg://yamp_dummy:qweasd123@localhost:5434/yamp_movies_db'
    # Параметры аутентификации
    reset_password_token_secret: SecretStr
    verification_token_secret: SecretStr

    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(__file__))

    log_level: str = LOG_LEVEL


settings = Settings(
    reset_password_token_secret='SECRET', verification_token_secret='SECRET'  # type: ignore
)


# Применяем настройки логирования
logging_config.dictConfig(get_logging_config(level=settings.log_level))
