# Base python image
FROM python:3.13-slim

# Running base required libraries
RUN pip install --no-cache-dir \
    torch \
    tensorflow \
    scikit-learn \
    numpy \
    boto3

WORKDIR /app