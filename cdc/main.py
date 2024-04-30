import json
from bson import json_util
from datetime import datetime

# set up the Google Cloud Logging python client library
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
# use Python’s standard logging library to send logs to GCP
import logging
cl = logging.getLogger()
file_handler = logging.FileHandler('log/cdc_{:%Y-%m-%d}.log'.format(datetime.now()))
formatter = logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
file_handler.setFormatter(formatter)
cl.addHandler(file_handler)

from rabbitmq import RabbitMQConnection
from mongodb import MongoDatabaseConnector
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def stream_process():
    """
    A function that processes changes in a specific MongoDB collection.
    It watches for changes, converts ObjectId to strings, serializes documents using json_util,
    and publishes the data to RabbitMQ. Logs any errors that occur.

    When registering a change stream, we specify the collection and what types of changes to listen to
    using the $match and a few other aggregation pipeline stages which limit the amount of data to receive.
    """
    try:
        
        # Setup MongoDB connection
        client = MongoDatabaseConnector()
        db = client[settings.DATABASE_NAME]
        logging.info("Connected to MongoDB.")

        # The core of the CDC pattern in MongoDB is realized through the watch method.
        # sets up a change stream to monitor for specific types of changes in the database.
        # In this case, it's configured to listen for insert operations in any collection within the database.
        changes = db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])
        for change in changes:
            """
            For each event, extract metadata like the data type (collection name) and the entry ID.
            Also reformat the document by removing the MongoDB-specific _id and appending the data type and entry ID.
            This formatting makes the data more usable for downstream processes.
            """
            data_type = change["ns"]["coll"]
            entry_id = str(change["fullDocument"]["_id"])  # Convert ObjectId to string
            change["fullDocument"].pop("_id")
            change["fullDocument"]["type"] = data_type
            change["fullDocument"]["entry_id"] = entry_id

            # Convert the transformed doc to a JSON string. This serialized data is ready to be sent to RabbitMQ.
            data = json.dumps(change["fullDocument"], default=json_util.default)
            logging.info(f"Change detected and serialized: {data}")

            # Send data to rabbitmq
            mq_connection = RabbitMQConnection()
            mq_connection.connect()
            mq_connection.publish_message(data=data, queue="mongo_data")
            logging.info("Data published to RabbitMQ.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    stream_process()