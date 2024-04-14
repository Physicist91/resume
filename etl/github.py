"""
The GithubCrawler extends the BaseCrawler class and uses the extract method to retrieve the desired repository.
"""

import os
import shutil
import subprocess
import tempfile

from etl.basecrawler import BaseCrawler
from documents import RepositoryDocument

# set up the Google Cloud Logging python client library
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
# use Python’s standard logging library to send logs to GCP
import logging


class GithubCrawler(BaseCrawler):

    model = RepositoryDocument

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png")):
        super().__init__()
        self._ignore = ignore

    def extract(self, link: str, **kwargs):
        logging.info(f"Starting scrapping GitHub repository: {link}")
        repo_name = link.rstrip("/").split("/")[-1]

        local_temp = tempfile.mkdtemp()

        try:
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])

            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])

            tree = {}
            for root, dirs, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(self._ignore):
                    continue

                for file in files:
                    if file.endswith(self._ignore):
                        continue
                    file_path = os.path.join(dir, file)
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        tree[file_path] = f.read().replace(" ", "")

            instance = self.model(
                name=repo_name, link=link, content=tree, owner_id=kwargs.get("user")
            )
            instance.save()

        except Exception:
            raise
        finally:
            shutil.rmtree(local_temp)

        logging.info(f"Finished scrapping GitHub repository: {link}")