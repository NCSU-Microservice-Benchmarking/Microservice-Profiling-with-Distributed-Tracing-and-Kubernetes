FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    pip install numpy && \
    pip install requests && \
    pip install flask  && \
    pip install flask_apscheduler && \
    pip install opentelemetry-exporter-jaeger-thrift && \
    pip install opentelemetry-api opentelemetry-sdk

COPY . /usr/src/pyserver

ENV FLASK_APP app.py

WORKDIR /usr/src/pyserver

# EXPOSE 5000

# CMD flask run --host=0.0.0.0 --port=5000 --with-threads