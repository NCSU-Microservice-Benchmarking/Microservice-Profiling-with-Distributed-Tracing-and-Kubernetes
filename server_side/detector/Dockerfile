FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    apt-get install -y ffmpeg libsm6 libxext6 && \
    apt-get install -y python3-tk && \
    pip install flask  && \
    pip install opentelemetry-exporter-jaeger-thrift && \
    pip install opentelemetry-api opentelemetry-sdk && \ 
    pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113 && \
    pip install -qr https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt  # install dependencies && \
    pip install opencv-python &&\
    pip install -r requirements.txt

COPY . /usr/src/pyserver

ENV FLASK_APP app.py

WORKDIR /usr/src/pyserver

# EXPOSE 5000

# CMD flask run --host=0.0.0.0 --port=5000 --with-threads