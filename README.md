# Resumify

### Your friendly job search assistant

*With Resumify, you can build tailored resume, cover letter, and much more to get that dream job.*

TODO (Kevin):

- Dispatch crawlers to Cloud Run
- Add crawler for RPubs
- Add crawler for Blogspot
- Ability to use papers, theses, certificates, etc as supporting documents/additional info.
- consider to use Firestore for easier integration with GCP services

TODO (Adrian):

- Make persona integration with the UI via vectordB
- Explore RAG to learn and copy user's writing styles
- Fine-tune LLM model to approximate user's writing style

## ETL

The general data collection steps are (each platform would have its own crawler put into Cloud Run):

- use selenium to crawl user profile
- use BeatifulSoup to parse the HTML
- clean & normalize the extracted HTML
- save the result to MongoDB

Tools used:

- The [MongoDB Atlas](https://cloud.mongodb.com/v2/660abf1ce806e029b03e3496#/overview) acts as NoSQL DB for the various sources.
- Google Chrome acts as the web browser. [Install](https://askubuntu.com/questions/1461513/help-with-installing-the-chrome-web-browser-22-04-2-lts) it on the VM.
- Chrome driver. Instruction [here](https://skolo.online/documents/webscrapping/#step-2-install-chromedriver)
- RabbitMQ: https://console.cloud.google.com/marketplace/product/google/rabbitmq3

Tricky bits:
- for LinkedIN scraping: if it says "Join LinkedIN" as the Name, it has hit an authwall.
- `bson` package should not be installed separately, it should be installed via pymongo.

Flow: crawlers (python) -> cloud build -> artifact registry -> cloud run

The CDC and message broker are deployed on GCE.

## Streaming

The streaming component ingests data from the message queue. The hierarchy of data models will be:

1. raw (inherits from base model)
2. cleaned (inherits from raw)
3. chunked (inherits from cleaned)
4. embedded (inherits from chunked)

Each data type (article, post, code) has their own class for the states 1-4. Each data type (and its state) is modeled using Pydantic models. The raw data (i.e. output from ETL) can be processed in one of two ways:

1. clean and store in NoSQL fashion
2. clean, chunk, and embed then stored using vector indices into a vector DB.

In both cases, the data will be stored into a vector DB (with or without vector indices) that acts as the feature store. Thus, we have two kinds of training data in the feature store:

1. cleaned data to create prompts and answers
2. chunked and embedded data for RAG

**Handler + dispatcher architecture**: use a [creational factory pattern](https://refactoring.guru/design-patterns/abstract-factory) to instantiate a handler implemented for that specific data type (post, article, code) and operation (cleaning, chunking, embedding). The handler follows the [strategy behavioral pattern](https://refactoring.guru/design-patterns/strategy). This allow us to process multiple types of data in a single streaming pipeline by leveraging polymorphism to isolate the logic for a given data type and operation.

The streaming pipeline can be deployed to GCP and we can use the freemium serverless version of Qdrant for the vector DB. This would need `qdrant-client`: https://github.com/qdrant/qdrant-client.

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

### Docker

Docker Setup

- Installation: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04
- Docker Compose Install: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04
- Docker Compose version: https://docs.docker.com/compose/compose-file/compose-versioning/
- Authenticate with Artifact Registry: https://cloud.google.com/artifact-registry/docs/docker/authentication

Docker commands:

- Tag your image: `docker tag anuks_mq:v001 asia-southeast1-docker.pkg.dev/civil-oarlock-418910/resumify-docker/anuks_mq:v001`
- Push to Artifact Registry: `docker push gcr.io/civil-oarlock-418910/[IMAGE:TAG]`

### Prompt Enginering

Best practices for prompting:
![image](https://github.com/Physicist91/resume/assets/4892798/4df43460-d9cd-41df-8f59-0dfdcf2f9af4)

Original article: https://cloud.google.com/vertex-ai/generative-ai/docs/chat/chat-prompts
