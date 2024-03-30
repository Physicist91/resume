# Resumify
### Tailored Resume Generator for Your Dream Job

Baseline steps for data collection (we can call it ETL pipeline):
- log in using user credentials
- use selenium to crawl user profile
- use BeatifulSoup to parse the HTML
- clean & normalize the extracted HTML
- save the normalized (but still raw) data to MongoDB (or any NoSQL DB that can store unstructured text data) 

Furthermore, we also need RabbitMQ to contain events of changes (any CRUD operation) to the MongoDB. We can deploy the ETL pipeline and the message queue service to GCP, and use freemium serverless version of MongoDB.

## Streaming

We need a streaming component to ingest data from the message queue. We can use Bytewax (Rust streaming engine with Python interface) to listen to the queue. The raw data (i.e. output from ETL) can be processed in one of two ways:
1. clean and store in NoSQL fashion
2. clean, chunk, and embed then stored using vector indices into a vector DB.

In both cases, the data will be stored into a vector DB (with or without vector indices) that acts as the feature store. Thus, we have two kinds of training data in the feature store:
1. cleaned data to create prompts and answers
2. chunked and embedded data for RAG

The streaming pipeline can be deployed to GCP and we can use either the freemium serverless version of Qdrant or Vertex AI Feature Store from GCP for the vector DB.

## Training

Components of the training pipeline:
- Data to prompt layer
- LLM fine-tuning module (e.g. with QLoRA) to fine tune Gemini
- Experiment tracker from GCP (or MLFlow or CometML)
- Evaluation using another LLM (e.g. GPT-4) to be logged into the experiment tracker

The best candidate LLM will be stored in the model registry. Manual inspection can still be done using prompt monitoring dashboard from MLFlow/CometML/TensorBoard. MLFlow is open-source, and CometML has a freemium version.

## Inference

Wrapped with REST API so that other users can interact with it through HTTP requests (similar to ChatGPT or Google).
- Features will be loaded from the feature store for RAG
- The fine-tuned LLM will be grabbed from the model registry based on its tag (i.e. accepted) and version (e.g. v0.0.1 or latest)
- The prompt layer will map the user query and retrieved docs from the vectorDB into a prompt

The user query can be as simple as the Job Description text (copied and paste e.g. from LinkedIN), or additionally to include some specific instructions.

Resumes generated from the LLM will be returned to the users and ideally be logged back into the prompt monitoring dashboard as well. We can use Vertex AI from GCP for the training and inference pipeline (may be a bit costly), or use Qwak for the deployment.
