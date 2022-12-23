import json
from pathlib import Path

from collector.collect import collect
from collector.function import Function
from config import Config, get_config
from generator.test_function import test_function
from setup import setup


def get_functions(conf: Config) -> list[Function]:
    stats_file = Path(conf.FUNC_STATS_FILE)
    if stats_file.exists():
        with stats_file.open(mode="r") as stream:
            return [Function.from_dict(x) for x in json.loads(stream.read())]

    functions = collect(conf)
    with stats_file.open(mode="w") as stream:
        json.dump([x.to_dict() for x in functions], stream)
    return functions


def write_vectors(func: Function, conf: Config):
    vectors = test_function(func, conf)
    with Path(conf.VECTORS_DIR, func.func_name).open(mode="w") as stream:
        json.dump(vars(vectors), stream)


def main():
    conf = get_config()
    setup(conf)
    functions = get_functions(conf)
    for func in functions:
        write_vectors(func, conf)


if __name__ == "__main__":
    main()
