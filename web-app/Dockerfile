FROM python:3.12-slim

EXPOSE 8080
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .


CMD ["streamlit", "run", "0 Home.py", "--server.port", "8080", "--server.address=0.0.0.0"]