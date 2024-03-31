"""
We created a base crawler class to respect the best software engineering practices.
For each data source, there would be separate crawlers created for the specific data characteristics (posts, articles, code, etc.).
Every crawler extends the BaseCrawler or BaseAbstractCrawler class, depending on the purpose.
- If need login and scrolling functionality, use the BaseAbstractCrawler.
- Use the BaseCrawler class for static crawler that doesn't need login, scroll page, or driver.
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from collector.documents import BaseDocument


class BaseCrawler:

    model: BaseDocument

    def extract(self, link: str, **kwargs):
        raise NotImplemented("Needs implementation in subclass.")


class BaseAbstractCrawler(BaseCrawler):

    def __init__(self, scroll_limit: int = 5):
        options = self.set_driver_options()

        self.scroll_limit = scroll_limit
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def set_driver_options(self) -> Options:
        return Options()

    def login(self):
        pass

    def scroll_page(self):
        """This Python code defines a method scroll_page that scrolls through a LinkedIn page
        by repeatedly scrolling to the bottom of the page and waiting for a few seconds.
        It keeps track of the current scroll position and stops when it reaches the specified scroll limit or when the page height no longer increases.
        """
        current_scroll = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or (
                self.scroll_limit and current_scroll >= self.scroll_limit
            ):
                break
            last_height = new_height
            current_scroll += 1