from os import getenv, path, getcwd
import logging
import logging.config
import dotenv
from typing import Any, Final, Dict
from app.utils.logging import ColorFormatter

dotenv.load_dotenv(path.join('.env'))

TG_BOT_TOKEN: str = getenv("TG_BOT_TOKEN", '')

DEBUG: bool = bool(int(getenv("DEBUG", 0)))
DEBUG_HOST, DEBUG_PORT = getenv("DEBUG_ADDR", '0.0.0.0:5678').split(':')
DEBUG_ARGV: list = [f"{getcwd()}/teachio.sh", '--dev','run']

DATABASE_URL: Final[str] = 'sqlite:///teachio.db'

DATABASE_CONFIG: Dict[str, Any] = {
    'db.url': DATABASE_URL,
    'db.echo': False,
}

LOGGING: Final[dict[str, Any]] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)s %(message)s', # %(name)s:%(lineno)s
            '()': ColorFormatter,
        },
        'db': {
            'format': '%(asctime)s [%(levelname)s] %(name)s %(message)s',
            '()': ColorFormatter
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler', 
            'formatter': 'basic'
        },
        'console_db':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'db'
        }
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'sqlalchemy.engine': {
            'handlers': ['console_db'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

logging.config.dictConfig(LOGGING)