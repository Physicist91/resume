"""
The feature pipeline streams/ingests multiple data types (e.g. article or code) from the queue and cleans and stores them in the feature store.
We implemented a dispatcher layer that knows how to apply data-specific operations based on the type of message.
"""

import bytewax.operators as op
from bytewax.dataflow import Dataflow

from input import RabbitMQSource
from output import QdrantOutput
from dispatchers import ChunkingDispatcher, CleaningDispatcher, EmbeddingDispatcher, RawDispatcher
from qdrant import connection

# define bytewax flow.
flow = Dataflow("Streaming pipeline.")

# Input node in the Bytewax graph.
stream = op.input("Read data from Queue.", flow, RabbitMQSource())

# The dispatcher layer uses a creational factory pattern to instantiate a handler
# map the JSON to a pydantic model
stream = op.map("Raw dispatch.", stream, RawDispatcher.handle_mq_message)

# apply data cleaning based on the specific type (posts, article, or code) -- strategy behavioral pattern
stream = op.map("Clean dispatch.", stream, CleaningDispatcher.dispatch_cleaner)

# load the cleaned data to vector DB
op.output(
    "Insert cleaned data to QDrant.",
    stream,
    QdrantOutput(connection=connection, sink_type="clean"),
)

# perform data chunking and flattening to 1-D list
stream = op.flat_map("Chunk dispatch.", stream, ChunkingDispatcher.dispatch_chunker)

# perform embedding of the chunks into vectors
stream = op.map(
    "Embedded chunk dispatch.", stream, EmbeddingDispatcher.dispatch_embedder
)

# output node for the Bytewax graph.
op.output(
    "Load augmented data to Vector DB.",
    stream,
    QdrantOutput(connection=connection, sink_type="vector"),
)