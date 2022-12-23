from dataclasses import dataclass

from collector.function import Function


@dataclass
class CodeInfo:
    code: str
    args: list[str]


def annotate_argument(arg_type: str, arg_idx: int) -> tuple[str, str]:
    arg_name = f"arg{arg_idx}"
    code = f"""{arg_type} {arg_name};
klee_make_symbolic(&{arg_name}, sizeof(arg_name), \"{arg_name} (type {arg_type})\");"""
    return arg_name, code


def main_function_code(func: Function) -> str:
    defs = ""
    args = []
    for idx, arg_type in enumerate(func.signature.args):
        name, decl = annotate_argument(arg_type, idx)
        args.append(name)
        defs += decl

    return "int main() { " + defs +\
        f"{func.func_name}({','.join(args)});" + "return 0; }"


def test_file_code(func: Function) -> CodeInfo:
    code = '#include "klee/klee.h"\n'
    if func.file_path.endswith(".h"):
        return CodeInfo(
            code + main_function_code(func),
            func.signature.args
        )
    assert False
