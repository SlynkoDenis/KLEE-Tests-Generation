from dataclasses import dataclass

from collector.function import Function
from config import Config
from generator.cmd import CommandExecutor
from generator.test_file_code import test_file_code
from generator.vectors_getter import TestVectorsGetter


@dataclass
class GeneratedTests:
    args_types: list[str]
    test_vectors: list[list[str]]
    coverage: str


class CompileBytecode(CommandExecutor):
    def __init__(self, conf: Config, bytecode_file: str | None = None):
        self.bytecode_file: str | None = bytecode_file
        super().__init__(conf)

    def _exec_impl(self, *args, **kwargs):
        filename: str = kwargs.pop("filename", "klee_test.c")
        if (bytecode_file := kwargs.pop("bytecode_file")):
            self.bytecode_file = bytecode_file
        super()._exec_impl(
            "clang-11",
            "-I",
            self._conf.KLEE_PATH,
            "-emit-llvm",
            "-c",
            "-g",
            "-O0",
            "-Xclang",
            "-disable-O0-optnone",
            filename,
            f"-o {self.bytecode_file}",
            *args,
            **kwargs
        )


class KleeRun(CommandExecutor):
    def _exec_impl(self, *args, **kwargs):
        bytecode_file = kwargs.pop(bytecode_file)
        return super()._exec_impl(
            f"{self._conf.KLEE_BIN_PATH}/klee",
            "-max-time=60s",
            bytecode_file
            *args,
            **kwargs
        )


class CoverageStatistics(CommandExecutor):
    def _exec_impl(self, *args, **kwargs):
        return super()._exec_impl(
            f"{self._conf.KLEE_BIN_PATH}/klee-stats",
            "klee-last",
            *args,
            **kwargs
        )


def test_function(
    func: Function,
    conf: Config,
    filename: str = "klee_test.c"
) -> GeneratedTests:
    func_test = test_file_code(func)
    with open(filename, mode="w") as stream:
        stream.write(func_test.code)

    bytecode_file = CompileBytecode(conf).execute(filename=filename).bytecode_file
    # TODO: link bytecodes if needed

    KleeRun(conf).execute(bytecode_file=bytecode_file)

    return GeneratedTests(
        func.signature.args,
        TestVectorsGetter(conf).get_vectors(),
        CoverageStatistics(conf).execute().output
    )
