# Resumify
### Tailored Resume Generator for Your Dream Job

Baseline steps for ETL pipeline:
- log in using user credentials
- use selenium to crawl user profile
- use BeatifulSoup to parse the HTML
- clean & normalize the extracted HTML
- save the normalized (but still raw) data to Mongo DB

Alternative to MongoDB is a NoSQL DB that can stored unstructured text data. We also need RabbitMQ to contain events of changes (any CRUD operation) to the MongoDB.

We can deploy the ETL pipeline and the message queue service to GCP, and use freemium serverless version of MongoDB.
