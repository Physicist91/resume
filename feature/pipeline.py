"""
The feature pipeline streams/ingests multiple data types (posts, articles, or code snapshots)
We implemented a dispatcher layer that knows how to apply data-specific operations based on the type of message.
"""

import bytewax.operators as op
from bytewax.dataflow import Dataflow

from feature.input import RabbitMQSource
from feature.output import QdrantOutput
from data_logic.dispatchers import (
    ChunkingDispatcher,
    CleaningDispatcher,
    EmbeddingDispatcher,
    RawDispatcher,
)
from db.qdrant import connection

# define bytewax flow
flow = Dataflow("Streaming ingestion pipeline")

# Read source from RabbitMQ: either posts, article, or code
stream = op.input("input", flow, RabbitMQSource())

# The dispatcher layer uses a creational factory pattern to instantiate a handler implemented for that specific data type (post, article, code) and operation (cleaning, chunking, embedding).
# The handler follows the strategy behavioral pattern.
# map the JSON to a pydantic model
stream = op.map("raw dispatch", stream, RawDispatcher.handle_mq_message)

# apply data cleaning based on the specific type (posts, article, or code)
stream = op.map("clean dispatch", stream, CleaningDispatcher.dispatch_cleaner)

# load the cleaned data to vector DB
op.output(
    "cleaned data insert to qdrant",
    stream,
    QdrantOutput(connection=connection, sink_type="clean"),
)

# perform data chunking and flattening to 1-D list
stream = op.flat_map("chunk dispatch", stream, ChunkingDispatcher.dispatch_chunker)

# perform embedding of the chunks into vectors
stream = op.map(
    "embedded chunk dispatch", stream, EmbeddingDispatcher.dispatch_embedder
)

# load the augmented data/vectors into the vectorDB
op.output(
    "embedded data insert to qdrant",
    stream,
    QdrantOutput(connection=connection, sink_type="vector"),
)