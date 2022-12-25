import argparse
import json
from pathlib import Path
import typing

from tqdm import tqdm

from collector.collect import collect
from collector.function import Function
from config import Config, get_config, setup
from generator.test_function import test_function


def get_functions(
    conf: Config,
    max_functions: typing.Optional[int]
) -> typing.List[Function]:
    stats_file = Path(conf.FUNC_STATS_FILE)
    if stats_file.exists():
        with stats_file.open(mode="r", encoding="utf-8") as stream:
            return [Function.from_dict(x) for x in json.loads(stream.read())]

    functions = collect(conf, max_count=max_functions)
    with stats_file.open(mode="w", encoding="utf-8") as stream:
        json.dump([x.to_dict() for x in functions], stream)
    return functions


def write_vectors(func: Function, conf: Config, save_temps: bool):
    vectors = test_function(func, conf, save_temps=save_temps)
    if vectors:
        path = Path(conf.VECTORS_DIR, f"{func.func_name}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(mode="w", encoding="utf-8") as stream:
            json.dump(vars(vectors), stream, indent=4)


def main(max_functions: typing.Optional[int], save_temps: bool):
    conf = get_config()
    setup(conf)

    functions = get_functions(conf, max_functions)
    for func in tqdm(functions):
        write_vectors(func, conf, save_temps)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="klee-test-gen",
    )
    parser.add_argument("--max-functions", type=int, default=None)
    parser.add_argument("--config", type=str, action="store", default="config.yaml")
    parser.add_argument("--save-temps", action="store_true", default=False)

    args = parser.parse_args()
    main(args.max_functions, args.save_temps)
