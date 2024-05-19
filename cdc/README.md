# Change Data Capture Service
### Self-contained implementation of CDC and RabbitMQ for deployment on Cloud Run

There are two main applications implemented here:

1. CDC: adds any change made to the Mongo DB to the queue.
2. queue: based on RabbitMQ, stores all the events until they are processed.