from dataclasses import dataclass


@dataclass
class Signature:
    static: bool
    return_type: str
    args: list[str]

    def __hash__(self):
        return hash((self.return_type, ", ".join(self.args),))

    def to_dict(self) -> dict:
        return {
            "static": self.static,
            "return_type": self.return_type,
            "args": self.args
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class Function:
    file_path: str
    func_name: str
    signature: Signature

    def __repr__(self) -> str:
        return (f"<Function(file_path='{self.file_path}', func_name='{self.func_name}', "
                f"signature='{self.signature}'>")

    def __hash__(self):
        return hash((self.func_name, self.signature,))

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "func_name": self.func_name,
            "signature": self.signature.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        data["signature"] = Signature.from_dict(data["signature"])
        return cls(**data)
