"""
The LinkedinCrawler extend the BaseAbstractCrawler (as they depend on the login and scrolling functionality).
"""

import os
import time
from typing import Dict, List

from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import settings
from etl.basecrawler import BaseAbstractCrawler
from documents import PostDocument, ProfileDocument

# set up the Google Cloud Logging python client library
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
# use Python’s standard logging library to send logs to GCP
import logging
#cl = logging.getLogger()
#file_handler = logging.FileHandler('log/linkedin_crawler.log')
#cl.addHandler(file_handler)

class LinkedInCrawler(BaseAbstractCrawler):

    model_post = PostDocument
    model_profile = ProfileDocument

    def set_driver_options(self) -> Options:
        options = Options()
        options.add_experimental_option("detach", True)
        return options

    def extract(self, link: str, **kwargs):
        """
        Extracts data for a given profile link by scraping various sections like name, about, main page, experience, and education. 
        Scrolls the page to extract posts, images, and their corresponding information. 
        Inserts the scraped posts into the database with the platform set as LinkedIn. 
        Logs the number of posts found and when the data scraping is finished. 

        Parameters:
        - link (str): The link to the profile to scrape data from.
        - **kwargs: Additional keyword arguments.

        Returns:
        None
        """
        print(f"Starting to scrape data for profile: {link}")

        #self.login()

        soup = self._get_page_content(link)
        
        data = {
            "Name": self._scrape_section(soup, "h1"),
            "About": self._scrape_section(soup, "div", class_="core-section-container__content break-words"),
            "Main Page": self._scrape_section(soup, "div", {"id": "main-content"}),
            "Experience": self._scrape_experience(soup),
            "Education": self._scrape_education(soup),
        }
        
        logging.info(f"scraped {data}")
        # Scrolling and scraping posts
        self.scroll_page()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        post_elements = soup.find_all(
            "div",
            class_="update-components-text relative update-components-update-v2__commentary",
        )
        buttons = soup.find_all("button", class_="update-components-image__image-link")
        post_images = self._extract_image_urls(buttons)

        posts = self._extract_posts(post_elements, post_images)
        logging.info(f"Found {len(posts)} posts for profile: {link}")

        self.driver.close()
        
        if len(posts) > 0:
            self.model_post.bulk_insert(
                [
                    PostDocument(
                        platform="linkedin", content=post, author_id=kwargs.get("user")
                    )
                    for post in posts
                ]
            )
        
        logging.info("Saving user info to DB..")
        
        try:
            instance = self.model_profile(platform="linkedin", content=data, link=link, user_id=kwargs.get("user"))
            instance.save()
        except:
            logging.error("Error saving to MongoDB.")
            raise Exception("Error when saving to MongoDB")
            
        logging.info(f"Finished scrapping data for profile: {link}")

    def _scrape_section(self, soup: BeautifulSoup, *args, **kwargs):
        """ finds a specific section in the LinkedIn profile represented by soup,
        extracts the text from it, and returns the text stripped of any leading or trailing whitespaces.
        If the section is not found, it returns an empty string"""
        # Example: Scrape the 'About' section
        parent_div = soup.find(*args, **kwargs)
        return parent_div.get_text(strip=True) if parent_div else ""

    def _extract_image_urls(self, buttons: List[Tag]) -> Dict[str, str]:
        """
        Extracts image URLs from button elements.

        Args:
            buttons (List[Tag]): A list of BeautifulSoup Tag objects representing buttons.

        Returns:
            Dict[str, str]: A dictionary mapping post indexes to image URLs.
        """
        post_images = {}
        for i, button in enumerate(buttons):
            img_tag = button.find("img")
            if img_tag and "src" in img_tag.attrs:
                post_images[f"Post_{i}"] = img_tag["src"]
            else:
                logging.warning("No image found in this button")
        return post_images

    def _get_page_content(self, url: str) -> BeautifulSoup:
        """Retrieve the page content of a given URL."""
        self.driver.get(url)
        
        # scroll to the bottom to load entire page
        start = time.time()
        initialScroll = 0
        finalScroll = 1000
        while True:
            self.driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
            # this command scrolls the window starting from
            # the pixel value stored in the initialScroll 
            # variable to the pixel value stored at the
            # finalScroll variable
            initialScroll = finalScroll
            finalScroll += 1000

            # we will stop the script for 3 seconds so that 
            # the data can load
            time.sleep(3)
            # You can change it as per your needs and internet speed
            end = time.time()
            # We will scroll for 20 seconds.
            # You can change it as per your needs and internet speed
            if round(end - start) > 20:
                break
        
        return BeautifulSoup(self.driver.page_source, "lxml")

    def _extract_posts(
        self, post_elements: List[Tag], post_images: Dict[str, str]
    ) -> Dict[str, Dict[str, str]]:
        """
        Extracts post texts and combines them with their respective images.

        Args:
            post_elements (List[Tag]): A list of BeautifulSoup Tag objects representing post elements.
            post_images (Dict[str, str]): A dictionary containing image URLs mapped by post index.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary containing post data with text and optional image URL.
        """
        posts_data = {}
        for i, post_element in enumerate(post_elements):
            post_text = post_element.get_text(strip=True, separator="\n")
            post_data = {"text": post_text}
            if f"Post_{i}" in post_images:
                post_data["image"] = post_images[f"Post_{i}"]
            posts_data[f"Post_{i}"] = post_data
        return posts_data

    def _scrape_experience(self, soup: BeautifulSoup, *args, **kwargs):
        """Scrapes the Experience section of the LinkedIn profile."""
        experience_content = soup.find('section', {'data-section': 'experience'})
        #experience_content = soup.find("section", {"id": "experience-section"})
        return experience_content.get_text(strip=True) if experience_content else ""

    def _scrape_education(self, soup: BeautifulSoup, *args, **kwargs) -> str:
        education_content = soup.find("section", {"data-section": "educationsDetails"})
        return education_content.get_text(strip=True) if education_content else ""
    
    def login(self):
        """Log in to LinkedIn."""
        self.driver.get("https://www.linkedin.com/login")
        if not settings.LINKEDIN_USERNAME and not settings.LINKEDIN_PASSWORD:
            raise Exception("Missing LinkedIn credentials. Please set LINKEDIN_USERNAME and LINKEDIN_PASSWORD in your environment.")
        
        time.sleep(5)
        self.driver.find_element(By.ID, "username").send_keys(
            settings.LINKEDIN_USERNAME
        )
        self.driver.find_element(By.ID, "password").send_keys(
            settings.LINKEDIN_PASSWORD
        )
        self.driver.find_element(
            By.CSS_SELECTOR, ".login__form_action_container"
            #By.XPATH, "//button[@type='submit']"
        ).click()