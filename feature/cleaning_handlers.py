"""
Hierarchy of classes used to map the raw data model to cleaned data model.
All our domain logic is modeled by a set of Handler() classes.
Here we implement the handlers for the cleaning logic.
"""

from abc import ABC, abstractmethod

from datamodels.base import DataModel
from datamodels.cleaned import ArticleCleanedModel, PostCleanedModel, RepositoryCleanedModel
from datamodels.raw import ArticleRawModel, PostsRawModel, RepositoryRawModel
from feature.cleaning_utils import clean_text


class CleaningDataHandler(ABC):
    """
    Abstract class for all cleaning data handlers.
    All data transformations logic for the cleaning step is done here
    """

    @abstractmethod
    def clean(self, data_model: DataModel) -> DataModel:
        pass


class PostCleaningHandler(CleaningDataHandler):
    """
    The handler used to map a PostsRawModel to a PostCleanedModel.
    """
    def clean(self, data_model: PostsRawModel) -> PostCleanedModel:
        return PostCleanedModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            cleaned_content=clean_text("".join(data_model.content.values())),
            author_id=data_model.author_id,
            image=data_model.image if data_model.image else None,
            type=data_model.type,
        )


class ArticleCleaningHandler(CleaningDataHandler):
    """
    Implementation of the handler used to clean an article.
    """
    def clean(self, data_model: ArticleRawModel) -> ArticleCleanedModel:
        return ArticleCleanedModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            link=data_model.link,
            cleaned_content=clean_text("".join(data_model.content.values())),
            author_id=data_model.author_id,
            type=data_model.type,
        )


class RepositoryCleaningHandler(CleaningDataHandler):
    """
    Implementation of the handler used to clean the code repository.
    """
    def clean(self, data_model: RepositoryRawModel) -> RepositoryCleanedModel:
        return RepositoryCleanedModel(
            entry_id=data_model.entry_id,
            name=data_model.name,
            link=data_model.link,
            cleaned_content=clean_text("".join(data_model.content.values())),
            owner_id=data_model.owner_id,
            type=data_model.type,
        )