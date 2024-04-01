from config import settings
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# set up the Google Cloud Logging python client library
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
# use Python’s standard logging library to send logs to GCP
import logging


class MongoDatabaseConnector:
    _instance: MongoClient | None = None

    def __new__(cls, *args, **kwargs) -> MongoClient:
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.DATABASE_HOST)
            except ConnectionFailure as e:
                logging.error(f"Couldn't connect to the database: {str(e)}")
                raise

        logging.info(
            f"Connection to database with uri: {settings.DATABASE_HOST} successful"
        )
        return cls._instance

    def close(self):
        if self._instance:
            self._instance.close()
            logging.info("Connected to database has been closed.")


connection = MongoDatabaseConnector()