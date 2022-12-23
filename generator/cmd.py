import subprocess

from config import Config


class SubprocessError(Exception):
    pass


class CommandExecutor:
    def __init__(self, conf: Config):
        self.output: str | None = None
        self.error: str | None = None
        self._conf = conf

    def execute(self, *args, **kwargs):
        process = self._exec_impl(*args, **kwargs)
        self.output, self.error = process.communicate()
        self.output.decode("utf-8")
        self.error.decode("utf-8")

        if process.returncode:
            raise SubprocessError(f"Code {process.returncode}: {self.error}")
        return self

    def _exec_impl(self, *args, **kwargs) -> subprocess.Popen:
        process = subprocess.Popen(
            list(args),
            stdout=kwargs.pop("stdout", subprocess.PIPE),
            stdin=kwargs.pop("stdin", subprocess.PIPE),
            stderr=kwargs.pop("stderr", subprocess.PIPE),
            **kwargs
        )
        return process
