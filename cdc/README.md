# Change Data Capture Service
### Self-contained implementation of CDC and RabbitMQ for deployment on GCE

There are two main applications implemented here:

1. CDC: adds any change made to the Mongo DB to the queue.
2. queue: based on RabbitMQ, stores all the events until they are processed.


The CDC service and message broker based on [RabbitMQ](https://console.cloud.google.com/marketplace/product/google/rabbitmq3) are deployed on GCE.
GCE system setup:
- You'll need to install `pip` on the GCE to install the libraries in `requirements.txt`. [guide](https://www.redhat.com/sysadmin/install-python-pip-linux)
- You'll need to make a directory called `log`.

Testing:
* Test send message to your queue by running `rabbitmq.py`.
* Test the CDC by running `cdc.py` and inserting new content to the MongoDB.

References:
https://stackoverflow.com/questions/25240822/connecting-to-a-rabbitmq-deployment-hosted-on-google-compute-engine