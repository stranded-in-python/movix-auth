from typing import Any

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DEFAULT_HANDLERS = ['console']

LOG_LEVEL = 'INFO'


def get_logging_config(
    level: str = LOG_LEVEL,
    format: str = LOG_FORMAT,
    handlers: list[str] = LOG_DEFAULT_HANDLERS,
) -> dict[str, Any]:
    """
    Get logging config in dict format
    """

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {'format': format},
            'default': {
                '()': 'uvicorn.logging.DefaultFormatter',
                'fmt': '%(levelprefix)s %(message)s',
                'use_colors': None,
            },
            'access': {
                '()': 'uvicorn.logging.AccessFormatter',
                'fmt': "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'default': {
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
            'access': {
                'formatter': 'access',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            '': {'handlers': handlers, 'level': level},
            'uvicorn.error': {'level': level},
            'uvicorn.access': {
                'handlers': ['access'],
                'level': level,
                'propagate': False,
            },
        },
        'root': {'level': level, 'formatter': 'verbose', 'handlers': handlers},
    }