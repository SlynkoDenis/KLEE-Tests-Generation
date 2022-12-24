from functools import lru_cache
import logging.config
import os
from pathlib import Path
import typing

# pylint: disable=no-name-in-module
from pydantic import BaseModel
from yaml import safe_load


class RepoInfo(BaseModel):
    NAME: str
    DIRNAME: str


class Config(BaseModel):
    REPOS_PATH: typing.ClassVar[str] = "collector/repos"

    KLEE_INCLUDE_PATH: typing.Optional[str]
    KLEE_BIN_PATH: typing.Optional[str]

    FUNC_STATS_FILE: str

    VECTORS_DIR: str

    SERVER: str

    USER: str

    REPOS: typing.Dict[str, RepoInfo]

    @classmethod
    def get_config(cls, filepath: str = "config.yaml"):
        with Path(filepath).open(mode="r", encoding="utf-8") as stream:
            config = safe_load(stream)
            return cls(**config)

    def get_repo_url(self, repo_name: str) -> str:
        return f"https://{self.SERVER}/{self.USER}/{repo_name}.git"


@lru_cache(maxsize=None)
def get_config(filepath: str = "config.yaml") -> Config:
    return Config.get_config(filepath=filepath)


def get_logger_config() -> dict:
    return {
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }


def setup(conf: Config):
    logging.config.dictConfig(get_logger_config())
    if conf.KLEE_BIN_PATH:
        os.environ["PATH"] = f"{os.environ['PATH']}:{conf.KLEE_BIN_PATH}"
