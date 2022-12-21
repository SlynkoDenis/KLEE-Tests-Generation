from collector.crawler import ReposCrawler
from collector.function import Function
from config import Config


def collect(conf: Config) -> list[Function]:
    crawler = ReposCrawler(conf)
    crawler.clone_repos()
    return list(set(
        f for funcs in crawler.iterate() for f in funcs
    ))
