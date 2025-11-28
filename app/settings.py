from os import getenv, path
import logging
import logging.config
import dotenv
from typing import Any, Final
from app.utils.logging import ColorFormatter

dotenv.load_dotenv(path.join('.env'))

PROD: bool = bool(int(getenv("IS_PROD", 0)))
TG_BOT_TOKEN: str = getenv("TG_BOT_TOKEN", '')

LOGGING: Final[dict[str, Any]] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': '%(asctime)s [%(levelname)s] %(message)s', # %(name)s:%(lineno)s
            '()': ColorFormatter,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler', 
            'formatter': 'basic'
        }
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING)