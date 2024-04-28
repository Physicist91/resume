"""
Use Langchain to chunk our text.
Overlapping your chunks is a common pre-indexing RAG technique, which helps to cluster chunks from the same document semantically.

We use a 2 step strategy using Langchain’s
1. RecursiveCharacterTextSplitter https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter/ 2. SentenceTransformersTokenTextSplitter https://python.langchain.com/docs/modules/data_connection/document_transformers/split_by_token/
"""

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

from config import settings


def chunk_text(text: str) -> list[str]:
    """
    Note: may need to tweak the separators, chunk_size, and chunk_overlap parameters for our different use cases.
    
    First chunking step:
    1. Split the text into paragraphs
    2. Split the paragraph into smaller chunks if they are over chunk_size characters
    3. chunk_overlap overlap between chunks
    
    Second chunking step:
    1. Ensure that each chunk fits the requirements for the embedding model
    2. Provides small overlap between chunks
    """
    
    # First chunking step
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"], chunk_size=500, chunk_overlap=0
    )
    text_split = character_splitter.split_text(text)

    # Second chunking step
    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=50,
        tokens_per_chunk=settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
        model_name=settings.EMBEDDING_MODEL_ID,
    )
    chunks = []

    for section in text_split:
        chunks.extend(token_splitter.split_text(section))

    return chunks