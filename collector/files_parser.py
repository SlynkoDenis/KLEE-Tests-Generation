from abc import ABC, abstractmethod
import logging
import typing

import clang.cindex

from collector.function import Function, Signature

logging.getLogger(__name__)


class BaseFunctionsParser(ABC):
    def __init__(self, cursor: clang.cindex.Cursor):
        self._cursor = cursor

    def __iter__(self):
        return self

    def __next__(self) -> Function:
        while True:
            node = next(self._cursor)
            func = self._get_function_node(node)
            if func:
                return func

    @abstractmethod
    def _get_function_node(self, node: clang.cindex.Cursor) -> typing.Optional[Function]:
        pass


class FunctionParser(BaseFunctionsParser):
    _SUPPORTED_PRIMITIVE_TYPES = (
        "char",
        "short",
        "int",
        "unsigned",
        "long",
        "float",
        "double"
    )

    def __init__(self, cursor: clang.cindex.Cursor, filename: str):
        self._filename = filename
        super().__init__(cursor)

    def _accepts_node(self, node: clang.cindex.Cursor) -> bool:
        return bool(
            node.kind == clang.cindex.CursorKind.FUNCTION_DECL
            and self._filename.endswith(node.location.file.name)
            and node.spelling != "main"
            and node.is_definition()
            and sum(
                1 for x in node.get_definition().get_tokens()
                if x.spelling == node.spelling
            ) > 0
        )

    def _args_valid(self, args: typing.List[str]) -> bool:
        return bool(
            args
            and all(
                any(x in arg_type for x in self._SUPPORTED_PRIMITIVE_TYPES)
                for arg_type in args
            )
            and "*" not in " ".join(args)
        )

    def _function_valid(self, func: Function) -> bool:
        return bool(
            func.signature.static is False
            and func.signature.return_type
            and self._args_valid(func.signature.args)
        )

    def _get_function_node(self, node: clang.cindex.Cursor) -> typing.Optional[Function]:
        try:
            if not self._accepts_node(node):
                return None

            func = Function(
                node.location.file.name,
                node.spelling,
                self._get_signature(node)
            )
            if self._function_valid(func):
                logging.debug(node.displayname)
                return func
        except Exception as exc:
            logging.error("Uncaught exception: %s", str(exc))
        return None

    @staticmethod
    def _get_signature(node: clang.cindex.Cursor) -> Signature:
        def_tokens = [x.spelling for x in node.get_definition().get_tokens()]
        static = bool(def_tokens[0] == "static")

        signature: str = node.displayname
        open_br = signature.find("(") + 1
        close_br = signature.find(")")
        assert open_br <= close_br
        return Signature(
            static,
            FunctionParser._get_return_type(node.spelling, def_tokens),
            signature[open_br:close_br].split(",")
        )

    @staticmethod
    def _get_return_type(
        func_name: str,
        def_tokens: typing.List[str]
    ) -> typing.Optional[str]:
        func_idx = [idx for idx, x in enumerate(def_tokens) if x == func_name]
        if not func_idx:
            return None
        return " ".join(def_tokens[:func_idx[0]])
