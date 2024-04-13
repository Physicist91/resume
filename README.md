# Resumify
### Tailored Resume Generator for Your Dream Job

TODO: 
- Dispatch crawlers to Cloud Run (Kevin)
- Add crawler for RPubs
- Ability to use papers, theses, certificates, etc as supporting documents/additional info.

Docker Compose version: https://docs.docker.com/compose/compose-file/compose-versioning/

RabbitMQ Service Setup
- Image: Uses RabbitMQ 3 with management plugin based on Alpine Linux.
- Container Name: anuks
- Ports: Exposes RabbitMQ on port 5673 for message queue communication and 15673 for management console access (default 5672 and 15672 respectively).
- Volumes: Maps local directories for RabbitMQ data and log storage, ensuring persistence and easy access to logs.

## ETL

Baseline steps for data collection (each platform would have its own crawler put into Cloud Run):
- log in using user credentials
- use selenium to crawl user profile
- use BeatifulSoup to parse the HTML
- clean & normalize the extracted HTML
- save the normalized (but still raw) data to MongoDB

Tools used:
- The [MongoDB Atlas](https://cloud.mongodb.com/v2/660abf1ce806e029b03e3496#/overview) acts as NoSQL DB for the various sources.
- Google Chrome acts as the web browser. [Install](https://askubuntu.com/questions/1461513/help-with-installing-the-chrome-web-browser-22-04-2-lts) it on the VM.
- Chrome driver. Instruction [here](https://skolo.online/documents/webscrapping/#step-2-install-chromedriver)

Future improvement:
- may also consider to use multiple replicas in the MongoDB replica set for availability, redundancy and fault tolerance. 

Note for LinkedIN scraping: if it says "Join LinkedIN" as the Name, it has hit an authwall.

Flow: crawlers (python) -> cloud build -> artifact registry -> cloud run

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

## References

Best practices for prompting:
![image](https://github.com/Physicist91/resume/assets/4892798/4df43460-d9cd-41df-8f59-0dfdcf2f9af4)

Original article: https://cloud.google.com/vertex-ai/generative-ai/docs/chat/chat-prompts
