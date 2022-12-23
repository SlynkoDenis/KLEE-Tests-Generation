from abc import ABC, abstractmethod
import logging

from collector.function import Function, Signature
import clang.cindex

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
    def _get_function_node(self, node: clang.cindex.Cursor) -> Function | None:
        pass


class FunctionParser(BaseFunctionsParser):
    def __init__(self, cursor: clang.cindex.Cursor, filename: str):
        self._filename = filename
        super().__init__(cursor)

    def _accepts_node(self, node: clang.cindex.Cursor) -> bool:
        return bool(
            node.kind == clang.cindex.CursorKind.FUNCTION_DECL
            and self._filename.endswith(node.location.file.name)
            and node.is_definition()
            and sum(
                1 for x in node.get_definition().get_tokens()
                if x.spelling == node.spelling
            ) > 0
        )

    def _get_function_node(self, node: clang.cindex.Cursor) -> Function | None:
        if not self._accepts_node(node):
            return None

        func = Function(
            node.location.file.name,
            node.spelling,
            self.get_signature(node)
        )
        if (
            func.signature.static
            or "" == (joined_args := " ".join(func.signature.args))
            or "struct " in joined_args
            or "*" in joined_args
        ):
            return None
        logging.debug(node.displayname)
        return func

    @staticmethod
    def get_signature(node: clang.cindex.Cursor) -> Signature:
        def_tokens = [x.spelling for x in node.get_definition().get_tokens()]
        static = bool(def_tokens[0] == "static")

        signature: str = node.displayname
        open_br = signature.find("(") + 1
        close_br = signature.find(")")
        assert open_br <= close_br
        return Signature(
            static,
            "",
            signature[open_br:close_br].split(",")
        )
