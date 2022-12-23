from functools import lru_cache
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel
from yaml import safe_load


class RepoInfo(BaseModel):
    NAME: str
    DIRNAME: str


class Config(BaseModel):
    KLEE_PATH: ClassVar[str] = "/home/huawei/Desktop/github/klee/include"
    KLEE_BIN_PATH: ClassVar[str] = "/home/huawei/Desktop/github/klee/build/bin"
    LIBCLANG_PATH: ClassVar[str] = "/usr/lib/llvm-14/lib/libclang-14.so.1"
    REPOS_PATH: ClassVar[str] = "collector/repos"

    FUNC_STATS_FILE: str

    VECTORS_DIR: str

    SERVER: str

    USER: str

    REPOS: dict[str, RepoInfo]

    @classmethod
    def get_config(cls, filepath: str = "config.yaml"):
        with Path(filepath).open() as stream:
            config = safe_load(stream)
            return cls(**config)

    def get_repo_url(self, repo_name: str) -> str:
        return f"https://{self.SERVER}/{self.USER}/{repo_name}.git"


@lru_cache
def get_config(filepath: str = "config.yaml") -> Config:
    return Config.get_config(filepath=filepath)
