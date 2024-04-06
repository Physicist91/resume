"""
We use Object Document Mapping (ODM) between the application and the document-based MongoDB.
The data modeling here creates specific document classes that mirror the structure of the MongoDB collections.
Each class define the schema for each data type we store.
Examples:
- UserDocument: users’ details
- ProfileDocument: user's basic profiles such as education/experience/etc.
- RepositoryDocument: repository metadata
- PostDocument: post content
- ArticleDocument: article information
"""

import uuid
from typing import List, Optional

from config import settings
from mongodb import connection
from pydantic import UUID4, BaseModel, ConfigDict, Field
from pymongo.errors import WriteError, OperationFailure

# set up the Google Cloud Logging python client library
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
# use Python’s standard logging library to send logs to GCP
import logging

_database = connection.get_database(settings.DATABASE_NAME)

class BaseDocument(BaseModel):
    """
    In our ODM approach to MongoDB, the key CRUD operations are implemented:
    - conversion: `to_mongo` transforms model instances into Mongo-DB recognised format
    - insertion: `save` uses PyMongo's `insert_one` for adding documents and returning the inserted ID
    - bulk operation: `bulk_insert` uses `insert_many` for adding multiple documents and returning their IDs
    - Upsertion: `get_or_create` either fetches and existing document or creates a new one
    - Validation and Transformation: uses PyDantic models
    """
    id: UUID4 = Field(default_factory=uuid.uuid4)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert "_id" (str object) into "id" (UUID object)."""
        if not data:
            return data

        id = data.pop("_id", None)
        return cls(**dict(data, id=id))

    def to_mongo(self, **kwargs) -> dict:
        """Convert "id" (UUID object) into "_id" (str object)."""
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(
            exclude_unset=exclude_unset, by_alias=by_alias, **kwargs
        )

        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        return parsed

    def save(self, **kwargs):
        """
        A function to save the current object to the database.

        Parameters:
            kwargs (dict): Additional keyword arguments for saving.

        Returns:
            ObjectId: The inserted ID if successful, None otherwise.
        """
        collection = _database[self._get_collection_name()]
        try:
            result = collection.insert_one(self.to_mongo(**kwargs))
            return result.inserted_id
        except WriteError as e:
            logging.error(f"Failed to insert document {e}")
            return None

    @classmethod
    def get_or_create(cls, **filter_options) -> Optional[str]:
        """
        A method to either retrieve an existing document from the collection based on filter_options
        or create a new one if it does not exist. Returns the ID of the document as a string if found,
        or returns the newly created instance. Returns None in case of an OperationFailure.
        
        Parameters:
            **filter_options: keyword arguments used to filter the document
        
        Returns:
            Optional[str]: ID of the document as a string if found, the newly created instance, or None
        """
        collection = _database[cls._get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                return str(cls.from_mongo(instance).id)
            new_instance = cls(**filter_options)
            new_instance = new_instance.save()
            return new_instance
        except OperationFailure as e:
            logging.error(f"Failed to retrieve document: {e}")
            return None


    @classmethod
    def bulk_insert(cls, documents: List, **kwargs) -> Optional[List[str]]:
        """
        A method to bulk insert documents into a collection.

        Parameters:
            documents (List): List of documents to insert.
            **kwargs: Additional keyword arguments.

        Returns:
            Optional[List[str]]: List of IDs of the inserted documents or None if insertion fails.
        """
        collection = _database[cls._get_collection_name()]
        try:
            result = collection.insert_many(
                [doc.to_mongo(**kwargs) for doc in documents]
            )
            return result.inserted_ids
        except WriteError as e:
            logging.error(f"Failed to insert document {e}")
            return None


    @classmethod
    def _get_collection_name(cls):
        """
        A method to get the name of the collection. Raises an exception if the Settings class or its name attribute is missing.
        Returns the name of the collection from the Settings class.
        """
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise Exception(
                "Document should define an Settings configuration class with the name of the collection."
            )

        return cls.Settings.name


class UserDocument(BaseDocument):

    first_name: str
    last_name: str

    class Settings:
        name = "users"


class ProfileDocument(BaseDocument):

    platform: str
    content: dict

    class Settings:
        name = "profile"


class RepositoryDocument(BaseDocument):

    name: str
    link: str
    content: dict
    owner_id: str = Field(alias="owner_id")

    class Settings:
        name = "repositories"


class PostDocument(BaseDocument):

    platform: str
    content: dict
    author_id: str = Field(alias="author_id")

    class Settings:
        name = "posts"


class ArticleDocument(BaseDocument):

    platform: str
    link: str
    content: dict
    author_id: str = Field(alias="author_id")

    class Settings:
        name = "articles"