import logging
import subprocess
import typing

from config import Config

logging.getLogger(__name__)


class SubprocessError(Exception):
    pass


class CommandExecutor:
    def __init__(self, conf: Config):
        self.output: typing.Optional[str] = None
        self.error: typing.Optional[str] = None
        self._conf = conf

    def execute(self, *args, **kwargs):
        proc = self._exec_impl(*args, **kwargs)
        self.output, self.error = proc.communicate()
        self.output.decode("utf-8")
        self.error.decode("utf-8")

        if proc.returncode:
            raise SubprocessError(f"Code {proc.returncode}:\n{self.error.decode('utf-8')}")
        return self

    def _exec_impl(self, *args, **kwargs) -> subprocess.Popen:
        logging.debug(args)
        return subprocess.Popen(
            list(args),
            stdout=kwargs.pop("stdout", subprocess.PIPE),
            stdin=kwargs.pop("stdin", subprocess.PIPE),
            stderr=kwargs.pop("stderr", subprocess.PIPE),
            **kwargs
        )
