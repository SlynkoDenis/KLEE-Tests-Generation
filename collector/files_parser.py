from abc import ABC, abstractmethod

from collector.function import Function, Signature
import clang.cindex


class BaseFunctionsParser(ABC):
    def __init__(self, cursor: clang.cindex.Cursor):
        self._cursor = cursor

    def __iter__(self):
        return self

    def __next__(self) -> Function:
        node = next(self._cursor)
        while not self._accepts_node(node):
            node = next(self._cursor)
        return self._get_function_node(node)

    @abstractmethod
    def _accepts_node(self, node: clang.cindex.Cursor) -> bool:
        pass

    @abstractmethod
    def _get_function_node(self, node: clang.cindex.Cursor) -> Function:
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

    def _get_function_node(self, node: clang.cindex.Cursor) -> Function:
        assert node.get_definition()
        print(node.displayname)
        return Function(
            node.location.file.name,
            node.spelling,
            self.get_signature(
                node.spelling,
                [x.spelling for x in node.get_definition().get_tokens()]
            )
        )

    @staticmethod
    def get_signature(func_name: str, def_tokens: list[str]) -> Signature:
        signature_end = [idx for idx, x in enumerate(def_tokens) if x == "{"]
        assert signature_end
        assert def_tokens[signature_end[0] - 1] == ")"

        return_type = [idx for idx, x in enumerate(def_tokens) if x == func_name]
        assert return_type
        assert return_type[0] < signature_end[0]
        assert def_tokens[return_type[0] + 1] == "("
        start_pos = 0 if def_tokens[0] != "static" else 1
        return Signature(
            " ".join(def_tokens[start_pos:return_type[0]]),
            " ".join(def_tokens[return_type[0]+1:signature_end[0]]).split(",")
        )
