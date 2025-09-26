import logging
import os
from logging.config import dictConfig

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")


def setup_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                },
                "uvicorn": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": LOG_LEVEL,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "filename": LOG_FILE,
                    "maxBytes": 5 * 1024 * 1024,  # 5MB
                    "backupCount": 3,
                    "encoding": "utf-8",
                    "level": LOG_LEVEL,
                },
            },
            "loggers": {
                "task_tracker": {
                    "handlers": ["console", "file"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
            },
            # базовый логгер (если где-то вызовут logging.info(...) без getLogger)
            "root": {"handlers": ["console", "file"], "level": LOG_LEVEL},
        }
    )

    # uvicorn-логгеры к нашему формату/уровню
    logging.getLogger("uvicorn").handlers.clear()
    logging.getLogger("uvicorn.error").handlers.clear()
    logging.getLogger("uvicorn.access").handlers.clear()
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        h = logging.StreamHandler()
        h.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )
        lg.addHandler(h)
        lg.setLevel(LOG_LEVEL)

    # немного приглушим болтливые либы
    logging.getLogger("httpx").setLevel(os.getenv("HTTPX_LOG_LEVEL", "WARNING"))
