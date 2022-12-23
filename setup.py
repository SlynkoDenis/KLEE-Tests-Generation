import clang.cindex
import logging.config

from config import Config


def get_logger_config() -> dict:
    return {
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG"
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"]
        }
    }


def setup(conf: Config):
    logging.config.dictConfig(get_logger_config())
    clang.cindex.Config.set_library_file(conf.LIBCLANG_PATH)
