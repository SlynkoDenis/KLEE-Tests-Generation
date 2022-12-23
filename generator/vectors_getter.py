from glob import glob
from pathlib import Path
import re

from config import Config
from generator.cmd import CommandExecutor


class VectorGetter(CommandExecutor):
    def _exec_impl(self, *args, **kwargs):
        filepath: str = kwargs.pop("filepath")
        assert filepath is not None
        return super()._exec_impl(
            f"{self._conf.KLEE_BIN_PATH}/ktest-tool",
            filepath,
            *args,
            **kwargs
        )


class TestVectorsGetter:
    def __init__(self, conf: Config, output_dir: str = "klee-last"):
        self._output_dir = output_dir
        self._getter = VectorGetter(conf)

    def get_vectors(self) -> list[str]:
        vectors = []
        files = glob(f"{self._output_dir}/*.ktest")
        for filename in files:
            self._getter.execute(filepath=str(Path(self._output_dir, filename)))
            vectors.append(self._parse_output(self._getter.output))
        return vectors

    @staticmethod
    def _parse_output(output: bytes) -> list[str]:
        output = output.decode("utf-8")
        data = []
        object_idx = 0
        while True:
            hex = re.findall(fr"object {object_idx}: hex : (0x[0-9a-f]+)", output)
            assert len(hex) <= 1
            if not hex:
                return data
            data.append(hex[0])
            object_idx += 1
