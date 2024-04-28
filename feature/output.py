"""
Load output data to vector DB.

For every type of operation (cleaned or embedded) we have to subclass the StatelessSinkPartition Bytewax class (although stateful option is also available).
An instance of the class will run on every partition defined within the Bytewax deployment.
To try first using a single partition per worker. The idea is to have the ability to scale the Bytewax pipeline horizontally by adding more partitions (and workers).
"""

from bytewax.outputs import DynamicSink, StatelessSinkPartition
from db.qdrant import QdrantDatabaseConnector
from datamodels.base import DBDataModel
from qdrant_client.http.api_client import UnexpectedResponse
from qdrant_client.models import Batch #https://qdrant.tech/documentation/concepts/points/


class QdrantOutput(DynamicSink):
    """
    Class that facilitates the connection to a Qdrant vector DB.
    Inherits from Bytewax's DynamicSink for the ability to create different sink sources (e.g, vector and non-vector collections)
    Reference https://docs.bytewax.io/stable/api/bytewax/bytewax.outputs.html
    """

    def __init__(self, connection: QdrantDatabaseConnector, sink_type: str):
        # inject a QDrant DB connector
        self._connection = connection
        self._sink_type = sink_type

        # create all required QDrant collections if they don't already exist
        try:
            self._connection.get_collection(collection_name="cleaned_posts")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_non_vector_collection(
                collection_name="cleaned_posts"
            )

        try:
            self._connection.get_collection(collection_name="cleaned_articles")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_non_vector_collection(
                collection_name="cleaned_articles"
            )

        try:
            self._connection.get_collection(collection_name="cleaned_repositories")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_non_vector_collection(
                collection_name="cleaned_repositories"
            )

        try:
            self._connection.get_collection(collection_name="vector_posts")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_vector_collection(collection_name="vector_posts")

        try:
            self._connection.get_collection(collection_name="vector_articles")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_vector_collection(collection_name="vector_articles")

        try:
            self._connection.get_collection(collection_name="vector_repositories")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_vector_collection(
                collection_name="vector_repositories"
            )

    def build(self, worker_index: int, worker_count: int) -> StatelessSinkPartition:
        """
        Build a data sink for every bytewax worker
        """
        if self._sink_type == "clean":
            return QdrantCleanedDataSink(connection=self._connection)
        elif self._sink_type == "vector":
            return QdrantVectorDataSink(connection=self._connection)
        else:
            raise ValueError(f"Unsupported sink type: {self._sink_type}")


class QdrantCleanedDataSink(StatelessSinkPartition):
    """
    Inherit from Bytewax's statelessSinkPartition to create cleaned data partition/worker for the QDrant DB.
    """
    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection

    def write_batch(self, items: list[DBDataModel]) -> None:
        """
        use Qdrant’s Batch method to upload all the available points at once so as to reduce the latency on the network I/O side.
        """
        #Serialize the data into a format accepted by the QDrant DB.
        payloads = [item.save() for item in items]
        ids, data = zip(*payloads)
        
        # get the collection name based on the data type
        collection_name = get_clean_collection(data_type=data[0]["type"])
        
        # load the ids, vectors, and metadata to the QDrant vector DB (here the vector is an empty dictionary)
        self._client.write_data(
            collection_name=collection_name,
            points=Batch(ids=ids, vectors={}, payloads=data),
        )


class QdrantVectorDataSink(StatelessSinkPartition):
    """
    inherits from Bytewax's statelessSinkPartition to create vector data partition/worker for the QDrant DB.
    """
    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection

    def write_batch(self, items: list[DBDataModel]) -> None:
        """
        use Qdrant’s Batch method to upload all the available points at once so as to reduce the latency on the network I/O side
        """
        
        #Serialize the data into a format accepted by the QDrant DB.
        payloads = [item.save() for item in items]
        ids, vectors, meta_data = zip(*payloads)
        
        # get the collection name based on the data type
        collection_name = get_vector_collection(data_type=meta_data[0]["type"])
        
        # load the ids, vectors, and metadata to the QDrant vector DB (here the vector is an empty dictionary)
        self._client.write_data(
            collection_name=collection_name,
            points=Batch(ids=ids, vectors=vectors, payloads=meta_data),
        )


def get_clean_collection(data_type: str) -> str:
    """
    helper function to get the collection name for clean data worker based on the datatype.
    """
    if data_type == "posts":
        return "cleaned_posts"
    elif data_type == "articles":
        return "cleaned_articles"
    elif data_type == "repositories":
        return "cleaned_repositories"
    else:
        raise ValueError(f"Unsupported data type: {data_type}")


def get_vector_collection(data_type: str) -> str:
    """
    helper function to get the collection name for vector data worker based on the datatype.
    """
    if data_type == "posts":
        return "vector_posts"
    elif data_type == "articles":
        return "vector_articles"
    elif data_type == "repositories":
        return "vector_repositories"
    else:
        raise ValueError(f"Unsupported data type: {data_type}")