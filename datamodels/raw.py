from typing import Optional

from models.base import DataModel


class RepositoryRawModel(DataModel):
    """
    Class for raw state of a Github code repo
    """
    entry_id: str
    name: str
    link: str
    content: dict
    owner_id: str
    type: str


class ArticleRawModel(DataModel):
    """
    Class for raw state of a Medium article
    """
    entry_id: str
    platform: str
    link: str
    content: dict
    author_id: str
    type: str


class PostsRawModel(DataModel):
    """
    Class for raw state of a LinkedIN post
    """
    entry_id: str
    platform: str
    content: dict
    author_id: str
    image: Optional[str] = None
    type: str