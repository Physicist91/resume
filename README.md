# Resumify
### Tailored Resume Generator for Your Dream Job

Baseline steps for data collection (we can call it ETL pipeline):
- log in using user credentials
- use selenium to crawl user profile
- use BeatifulSoup to parse the HTML
- clean & normalize the extracted HTML
- save the normalized (but still raw) data to Mongo DB

Alternative to MongoDB is a NoSQL DB that can stored unstructured text data. We also need RabbitMQ to contain events of changes (any CRUD operation) to the MongoDB. We can deploy the ETL pipeline and the message queue service to GCP, and use freemium serverless version of MongoDB.

## Streaming

We need a streaming component to ingest data from the message queue. We can use Bytewax (Rust streaming engine with Python interface) to listen to the queue. The raw data (i.e. output from ETL) can be processed in one of two ways:
1. clean and store in NoSQL fashion
2. clean, chunk, and embed then stored using vector indices into a vector DB.

In both cases, the data will be stored into a vector DB (with or without vector indices) that acts as the feature store. Having two snapshots of data would let us finetune our LLM on standard and augmented prompts. The streaming pipeline can be deployed to GCP and we can use either the freemium serverless version of Qdrant or Vertex AI from GCP for the vector DB.
