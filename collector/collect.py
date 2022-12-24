import typing

from collector.crawler import ReposCrawler
from collector.function import Function
from config import Config


def collect(
    conf: Config,
    max_count: typing.Optional[int] = None
) -> typing.List[Function]:
    crawler = ReposCrawler(conf)
    crawler.clone_repos()

    res = []
    for functions in crawler.iterate():
        for func in functions:
            res.append(func)
            if max_count and len(res) >= max_count:
                return res
    return res
