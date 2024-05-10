# Use the official Python image
FROM python:3.9-slim

WORKDIR /app

# Set PYTHONUNBUFFERED environment variable
ENV PYTHONUNBUFFERED=1

COPY main.py .
COPY crud.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
