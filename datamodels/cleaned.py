from typing import Optional, Tuple

from models.base import DBDataModel


class PostCleanedModel(DBDataModel):
    """
    Class for the cleaned state of a LinkedIN post
    """
    entry_id: str
    platform: str
    cleaned_content: str
    author_id: str
    image: Optional[str] = None
    type: str

    def save(self) -> Tuple[str, dict]:
        data = {
            "platform": self.platform,
            "author_id": self.author_id,
            "cleaned_content": self.cleaned_content,
            "image": self.image,
            "type": self.type,
        }

        return self.entry_id, data


class ArticleCleanedModel(DBDataModel):
    """
    Class for the cleaned state of a medium article.
    """
    entry_id: str
    platform: str
    link: str
    cleaned_content: str
    author_id: str
    type: str

    def save(self) -> Tuple[str, dict]:
        data = {
            "platform": self.platform,
            "link": self.link,
            "cleaned_content": self.cleaned_content,
            "author_id": self.author_id,
            "type": self.type,
        }

        return self.entry_id, data


class RepositoryCleanedModel(DBDataModel):
    """
    Class for the cleaned state of a Github repo.
    """
    entry_id: str
    name: str
    link: str
    cleaned_content: str
    owner_id: str
    type: str

    def save(self) -> Tuple[str, dict]:
        data = {
            "name": self.name,
            "link": self.link,
            "cleaned_content": self.cleaned_content,
            "owner_id": self.owner_id,
            "type": self.type,
        }

        return self.entry_id, data