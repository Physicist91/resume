from abc import ABC, abstractmethod

from pydantic import BaseModel


class DataModel(ABC, BaseModel):
    """
    Base abstract class for all data models to use the same parent class across all components.
    """

    entry_id: int
    type: str


class DBDataModel(DataModel):
    """
    Abstract class for all data models that need to be serialized and saved into a vector DB
    Afterward, we define a hierarchy of Pydantic models for:
    - all our data types: posts, articles, or code
    - all our states: raw, cleaned, chunked, and embedded
    """

    entry_id: int
    type: str

    @abstractmethod
    def save(self) -> tuple:
        pass