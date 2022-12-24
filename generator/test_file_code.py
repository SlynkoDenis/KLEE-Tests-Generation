from pathlib import Path
import typing

from collector.function import Function


class CodeInfo:
    def __init__(self, filename: str, code: str, args: typing.List[str]):
        self.filename: str = filename
        self.code: str = code
        self.args: typing.List[str] = args


def annotate_argument(arg_type: str, arg_idx: int) -> typing.Tuple[str, str]:
    arg_name = f"arg{arg_idx}"
    code = f"""{arg_type} {arg_name};
klee_make_symbolic(&{arg_name}, sizeof({arg_name}), \"{arg_name} (type {arg_type})\");"""
    return arg_name, code


def main_function_code(func: Function) -> str:
    defs = ""
    args = []
    for idx, arg_type in enumerate(func.signature.args):
        name, decl = annotate_argument(arg_type, idx)
        args.append(name)
        defs += decl

    return "int main() {\n" + defs +\
        f"{func.func_name}({','.join(args)});" + "\nreturn 0;\n}\n"


def test_file_code(func: Function, main_filename: str) -> typing.Tuple[CodeInfo, CodeInfo]:
    main = CodeInfo(
        main_filename,
        f'#include "klee/klee.h"\n{main_function_code(func)}',
        func.signature.args
    )

    header = None
    if func.file_path.endswith(".c"):
        header_name = Path(main_filename).parent / f"{func.func_name}.h"
        header_code = f"""#pragma once
#include <stdint.h>
{func.signature.return_type} {func.func_name}({', '.join(func.signature.args)});
"""
        header = CodeInfo(header_name, header_code, [])
        main.code = f'#include "{header_name}"\n{main.code}'

    return main, header
