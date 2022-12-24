import logging
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import typing

from collector.function import Function
from config import Config
from generator.cmd import CommandExecutor, SubprocessError
from generator.test_file_code import CodeInfo, test_file_code
from generator.vectors_getter import TestVectorsGetter

logging.getLogger(__name__)


class GeneratedTests:
    def __init__(
        self,
        source_path: str,
        args_types: typing.List[str],
        test_vectors: typing.List[typing.List[str]],
        coverage: str
    ):
        self.source_path: str = source_path
        self.args_types: typing.List[str] = args_types
        self.test_vectors: typing.List[typing.List[str]] = test_vectors
        self.coverage: str = coverage


class LinkBytecodes(CommandExecutor):
    def _exec_impl(self, *args, **kwargs):
        return super()._exec_impl(
            "llvm-link-11",
            *args,
            **kwargs
        )


class CompileBytecode(CommandExecutor):
    def __init__(self, conf: Config, bytecode_file: str):
        self.bytecode_file: str = bytecode_file
        super().__init__(conf)

    def _exec_impl(self, *args, **kwargs):
        t_units: typing.List[str] = kwargs.pop("t_units")
        assert t_units is not None

        cmd_args = ["clang-11"]
        if self._conf.KLEE_INCLUDE_PATH:
            cmd_args += ["-I", self._conf.KLEE_INCLUDE_PATH]
        cmd_args += [
            "-emit-llvm",
            "-c",
            "-g",
            "-O0",
            "-Xclang",
            "-disable-O0-optnone",
            *t_units,
        ]
        if len(t_units) == 1:
            cmd_args.extend(["-o", self.bytecode_file])
        return super()._exec_impl(
            *cmd_args,
            *args,
            **kwargs
        )


class KleeRun(CommandExecutor):
    def _exec_impl(self, *args, **kwargs):
        return super()._exec_impl(
            "klee",
            "-posix-runtime",
            "-max-time=60s",
            *args,
            **kwargs
        )


class CoverageStatistics(CommandExecutor):
    def _exec_impl(self, *args, **kwargs):
        return super()._exec_impl(
            "klee-stats",
            *args,
            **kwargs
        )


def compile_bytecode(t_units: typing.List[str], conf: Config) -> str:
    dirpath = Path(t_units[0]).parent
    bytecode_file = CompileBytecode(
        conf,
        str(dirpath / "klee_test.bc"),
    ).execute(t_units=t_units, cwd=str(dirpath)).bytecode_file

    if len(t_units) > 1:
        t_units = [f"{dirpath / Path(x).stem}.bc" for x in t_units]
        LinkBytecodes(conf).execute(*t_units, "-o", bytecode_file)
    return bytecode_file


def copy_with_header(header: CodeInfo, code_filepath: str) -> str:
    with Path(header.filename).open(mode="w", encoding="utf-8") as stream:
        stream.write(header.code)

    copy_file = Path(header.filename).parent / f"{Path(code_filepath).stem}_copy.c"
    shutil.copy(code_filepath, str(copy_file))
    with copy_file.open(mode="r+", encoding="utf-8") as stream:
        content = stream.read()
        stream.seek(0, 0)
        stream.write(f'#include "{header.filename}"\n{content}')
    return str(copy_file)


def __test_function_impl(
    func: Function,
    conf: Config,
    dirpath: str,
    filename: str
) -> typing.Optional[GeneratedTests]:
    dirpath = Path(dirpath)
    main_file = dirpath / filename
    func_test, header = test_file_code(func, str(main_file))
    with main_file.open(mode="w") as stream:
        stream.write(func_test.code)

    t_units = [func_test.filename]
    if header:
        copy_filename = copy_with_header(header, func.file_path)
        t_units.append(copy_filename)

    try:
        bytecode_file = compile_bytecode(t_units, conf)
        KleeRun(conf).execute(bytecode_file)
        output_dir = dirpath / "klee-last"
        return GeneratedTests(
            func.file_path,
            func.signature.args,
            TestVectorsGetter(conf, output_dir=str(output_dir)).get_vectors(),
            CoverageStatistics(conf).execute(str(output_dir)).output.decode("utf-8")
        )
    except SubprocessError as exc:
        logging.debug("Compilation failed: %s", str(exc))
        return None


def test_function(
    func: Function,
    conf: Config,
    filename: str = "klee_test.c",
    save_temps: bool = False
) -> typing.Optional[GeneratedTests]:
    if save_temps:
        return __test_function_impl(func, conf, ".", filename)
    with TemporaryDirectory() as dirname:
        return __test_function_impl(func, conf, dirname, filename)
