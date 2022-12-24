import glob
import logging
from pathlib import Path
import typing

from git import Repo
import clang.cindex

from config import Config
from collector.files_parser import BaseFunctionsParser, FunctionParser

logging.getLogger(__name__)


class ReposCrawler:
    def __init__(self, conf: Config):
        self._conf = conf
        self._index = clang.cindex.Index.create()
        self._repos: typing.Dict[str, Path] = {}

    def clone_repos(self):
        repos_path = Path(self._conf.REPOS_PATH)
        repos_path.mkdir(parents=True, exist_ok=True)

        for repo_info in self._conf.REPOS.values():
            self._repos[repo_info.NAME] = repos_path / repo_info.DIRNAME / repo_info.NAME
            if not self._repos[repo_info.NAME].exists():
                logging.info("Cloning repo %s...", repo_info.NAME)
                Repo.clone_from(
                    self._conf.get_repo_url(repo_info.NAME),
                    self._repos[repo_info.NAME],
                    multi_options=["--single-branch", "--depth=1"]
                )

    def iterate(self) -> BaseFunctionsParser:
        for repo_path in self._repos.values():
            for file in glob.iglob(f"{repo_path}/**/*", recursive=True):
                if file.endswith(".h") or file.endswith(".c"):
                    try:
                        children_tokens = self._index.parse(file).cursor.get_children()
                    except clang.cindex.TranslationUnitLoadError:
                        continue

                    yield FunctionParser(
                        children_tokens,
                        file
                    )
