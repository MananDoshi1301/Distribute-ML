# Base python image
FROM python:3.10-slim

# Running base required libraries
RUN pip install --no-cache-dir \
    numpy \
    scikit-learn \
    tensorflow \
    torch \
    torchvision \
    boto3


RUN  pip install --no-cache-dir mysql-connector-python \
&& pip list

WORKDIR /app