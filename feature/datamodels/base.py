"""
Each data type (and its state) will be modeled using Pydantic models.

Wee define a hierarchy of Pydantic models for:
    - all our data types: posts, articles, or code
    - all our states: raw, cleaned, chunked, and embedded
"""

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
    """

    entry_id: int
    type: str

    @abstractmethod
    def save(self) -> tuple:
        pass