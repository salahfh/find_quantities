import logging
import logging.config
from pathlib import Path

config_dict = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "minimal": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "minimal",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f'{Path.home() / "find_quantity.log"}',
            "formatter": "default",
            "maxBytes": 1024 * 10,
            "backupCount": 0,
        },
    },
    "loggers": {
        "find_quantity": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False,
        },
        "find_quantity.cli": {
            "level": "INFO",
            "handlers": ["console"],
        },
    },
}

logging.config.dictConfig(config_dict)
logger = logging.getLogger("find_quantity.cli")
