"""
call an embedding model to create our vectors.
"""

from InstructorEmbedding import INSTRUCTOR
from sentence_transformers.SentenceTransformer import SentenceTransformer

from config import settings


def embed_text(text: str):
    # embedding model used for posts and articles
    # a lightweight embedding model that can easily run in real-time on a 2 vCPU machine.
    # https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model.encode(text)


def embed_repositories(text: str):
    # embedding model used for the code repositories
    # This embedding model can be customized on the fly with instructions based on your particular data.
    # This allows the embedding model to specialize on your data without fine-tuning: good for embedding pieces of code.
    # https://huggingface.co/hkunlp/instructor-xl
    model = INSTRUCTOR("hkunlp/instructor-xl")
    sentence = text
    instruction = "Represent the structure of the repository"
    return model.encode([instruction, sentence])