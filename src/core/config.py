import os
from logging import config as logging_config

from pydantic import SecretStr
from pydantic.env_settings import BaseSettings

from core.logger import LOG_LEVEL, get_logging_config


class ModelConfig:
    allow_population_by_field_name = True


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = 'movix-auth'

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
    google_oauth_client_id: SecretStr = SecretStr("SECRET")
    google_oauth_client_secret: SecretStr = SecretStr("SECRET")
    state_secret: SecretStr = SecretStr("SECRET")
    reset_password_token_secret: SecretStr = SecretStr('reset_password')
    verification_password_token_secret: SecretStr = SecretStr('verify_password')
    access_token_secret: SecretStr = SecretStr('access_token')
    refresh_token_secret: SecretStr = SecretStr('refresh_token')

    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(__file__))

    log_level: str = LOG_LEVEL

    jaeger_host = 'jaeger'
    jaeger_port = 6831
    jaeger_enabled = False
    tracer_enabled = False
    rate_limits = False

    # notifications
    url_notification_event_registration_on: str = (
        "http://localhost:8005/api/v1/notification/events/registration/on"
    )
    sentry_dsn_auth: str = ""


settings = Settings()  # type: ignore

if settings.sentry_dsn_auth:
    import sentry_sdk

    sentry_sdk.init(dsn=settings.sentry_dsn_auth, traces_sample_rate=1.0)


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
