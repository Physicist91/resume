import re

from basecrawler import BaseCrawler


class CrawlerDispatcher:
    """
    In order to trigger cloud run, a python dispatcher is used to manage the crawlers for specific domains.
    - A crawler is to be registered for each domain.
    - Use the get_crawler method to get the appropriate crawler for a given URL.
    """
    def __init__(self) -> None:
        self._crawlers = {}

    def register(self, domain: str, crawler: type[BaseCrawler]) -> None:
        self._crawlers[r"https://(www\.)?{}.com/*".format(re.escape(domain))] = crawler

    def get_crawler(self, url: str) -> BaseCrawler:
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler()
        else:
            raise ValueError("No crawler found for the provided link")