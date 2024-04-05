"""
This main function defines a handler to put a crawler on a Cloud Run function.
The handler function is the entry point for Cloud Run. In Cloud Run, the handler function is invoked when an event triggers it.
"""

from typing import Any
import lib
# set up the Google Cloud Logging python client library
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
# use Python’s standard logging library to send logs to GCP
import logging

from github import GithubCrawler
from linkedin import LinkedInCrawler
from medium import MediumCrawler
from dispatcher import CrawlerDispatcher
from documents import UserDocument

_dispatcher = CrawlerDispatcher()
_dispatcher.register("medium", MediumCrawler)
_dispatcher.register("linkedin", LinkedInCrawler)
_dispatcher.register("github", GithubCrawler)


def handler(event) -> dict[str, Any]:
    first_name, last_name = lib.user_to_names(event.get("user"))
    
    user = UserDocument.get_or_create(first_name=first_name, last_name=last_name)

    link = event.get("link")
    crawler = _dispatcher.get_crawler(link)

    try:
        crawler.extract(link=link, user=user)

        return {"statusCode": 200, "body": "Link processed successfully"}
    except Exception as e:
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    """
    # Development only: run "python main.py" and test locally
    """
    event = {
        "user": "Kevin Siswandi",
        "link": "https://www.linkedin.com/in/kevinsiswandi/",
    }
    handler(event)