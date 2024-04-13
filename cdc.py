import json
import logging

from bson import json_util

from queue import publish_to_rabbitmq
from mongodb import MongoDatabaseConnector
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def stream_process(database_name: str):
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
        db = client[database_name]
        logging.info("Connected to MongoDB.")

        # Watch changes in a specific collection
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
            publish_to_rabbitmq(queue_name="test_queue", data=data)
            logging.info("Data published to RabbitMQ.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    stream_process()