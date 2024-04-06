# set up the Google Cloud Logging python client library
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
# use Python’s standard logging library to send logs to GCP
import logging

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from basecrawler import BaseAbstractCrawler
from documents import ArticleDocument


class MediumCrawler(BaseAbstractCrawler):
    model = ArticleDocument

    def set_extra_driver_options(self, options) -> None:
        options.add_argument(r"--profile-directory=Profile 2")

    def extract(self, link: str, **kwargs) -> None:
        """
        Extracts data from a Medium article link.
        
        Parameters:
            link (str): The link to the Medium article.
            **kwargs: Additional keyword arguments.
        
        Returns:
            None
        """
        logging.info(f"Starting scrapping Medium article: {link}")

        self.driver.get(link)
        self.scroll_page()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        title = soup.find_all("h1", class_="pw-post-title")
        subtitle = soup.find_all("h2", class_="pw-subtitle-paragraph")

        data = {
            "Title": title[0].string if title else None,
            "Subtitle": subtitle[0].string if subtitle else None,
            "Content": soup.get_text(),
        }

        logging.info(f"Successfully scraped and saved article: {link}")
        self.driver.close()
        instance = self.model(
            platform="medium", content=data, link=link, author_id=kwargs.get("user")
        )
        instance.save()

    def login(self):
        """Log in to Medium with Google"""
        self.driver.get("https://medium.com/m/signin")
        self.driver.find_element(By.TAG_NAME, "a").click()