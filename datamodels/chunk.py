from typing import Optional

from models.base import DataModel


class PostChunkModel(DataModel):
    """
    Class for the chunked state of a LinkedIN post.
    """
    entry_id: str
    platform: str
    chunk_id: str
    chunk_content: str
    author_id: str
    image: Optional[str] = None
    type: str


class ArticleChunkModel(DataModel):
    """
    Class for the chunked state of a medium article.
    """
    entry_id: str
    platform: str
    link: str
    chunk_id: str
    chunk_content: str
    author_id: str
    type: str


class RepositoryChunkModel(DataModel):
    """
    Class for the chunked state of a code repository.
    """
    entry_id: str
    name: str
    link: str
    chunk_id: str
    chunk_content: str
    owner_id: str
    type: str