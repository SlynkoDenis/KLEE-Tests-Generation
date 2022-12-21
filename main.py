import json
from pathlib import Path

from collector.collect import collect
from config import get_config
from setup import setup


def main():
    conf = get_config()
    setup(conf)
    functions = collect(conf)
    with Path(conf.FUNC_STATS_FILE).open(mode="w") as stream:
        json.dump([x.to_dict() for x in functions], stream)


if __name__ == "__main__":
    main()
