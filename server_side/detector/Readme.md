# To deploy the pyServer as a Kubernetes pod
1. Make sure the server is installed with [Docker](https://docs.docker.com/engine/install/ubuntu/) and [Kubernetes](https://kubernetes.io/docs/tasks/tools/)
2. In current folder, run 
    ```
    kubectl apply -f ./deploy_pyserver.yaml
    ```
3. Setup port forwarding (personally, I prefer to do it in a [tmux](https://github.com/tmux/tmux/wiki) session)  
    ```
    kubectl port-forward --address 0.0.0.0  svc/pyserver 5000:5000
    ```


# Develop a python application

1. Create a new folder for the application
2. Develop the application as usual in the created folder
3. Remember all the required packages or export the required packages by 
    
    ```bash
    pip freeze > requirements.txt
    ```
    

# Make a docker image

1. Register a docker hub account at: [https://hub.docker.com/](https://hub.docker.com/), remember your username and password.  
2. Create a file named `Dockerfile` in the application folder
3. Code the Dockerfile according to the following example
    
    ```docker
    FROM ubuntu:20.04 # base environment

    ARG DEBIAN_FRONTEND=noninteractive # disable interactive commandline pop up

    RUN apt-get update && \ # install dependencies
        apt-get install -y python3 && \
        apt-get install -y python3-pip && \
        apt-get install -y ffmpeg libsm6 libxext6 && \
        pip install flask  && \
        pip install opentelemetry-exporter-jaeger-thrift && \
        pip install opentelemetry-api opentelemetry-sdk && \ 
        pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu  && \
        pip install -qr https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt  && \
        pip install opencv-python

    COPY . /usr/src/pyserver # copy file from folder to docker container  

    ENV FLASK_APP app.py   # set environment variables in the container, similar to export FLASK_APP=pyServer.py  

    WORKDIR /usr/src/pyserver  # set current worker directory, similar to cd /usr/src/pyserver

    EXPOSE 5000

    CMD flask run --host=0.0.0.0 --port=5000 --with-threads
    ```
    
4. log in to your docker account on the machine
    
    ```bash
    sudo docker login --username=your_username --password=your_password
    ```
    
5. restart the docker service
    
    ```bash
    sudo service docker restart
    ```
    
6. build the docker image
    
    ```bash
    sudo docker build -t your_username/your-app-name:app-version ./your-app-folder
    ```
    
7. push the docker image to your docker repository
    
    ```bash
    sudo docker push your_username/your-app-name:app-version
    ```
    

# Deploy the Docker image on Kubernetes

1. Create a Kubernetes configuration file named `deploy_your-app-name.yaml` following the template below
    
    ```bash
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: your-app-name
      labels:
        name: your-app-name
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: your-app-name
      template:
        metadata:
          labels:
            app: your-app-name
        spec:
          containers:
            - name: your-app-name
              image: your_username/your-app-name:app-version
              imagePullPolicy: Always
              ports:
                - name: your-app-name
                  containerPort: port-to-use
                  protocol: TCP-or-UDP
    ---
    apiVersion: v1
    kind: Service
    metadata:
        name: your-app-name
    spec:
        selector:
            app: your-app-name
        ports:
            - protocol: TCP-or-UDP
              port: port-to-use
              targetPort: port-to-use
    ```
    
2. Deploy the Docker image
    
    ```bash
    kubectl apply -f ./deploy_your-app-name.yaml
    ```
    
3.  Set port forward, run this command in the background by add a `&` at the end of the command or using tmux
    
    ```bash
    kubectl port-forward --address public_ip_to_expose(usually 0.0.0.0)  pod/pod_name internal_port:external_port
    ```
    
    or
    
    ```bash
    kubectl port-forward --address public_ip_to_expose(usually 0.0.0.0)  svc/service_name internal_port:external_port
    ```
    

# Deploy a python application with Jaeger tracing on Kubernetes

The process is similar with deploy a common python application. Major changes are included in the following 3 aspects

- In the Python script: import required packages, add config, and instantiate Jaeger tracer
    
    ```python
    from flask import request
    from flask import Flask
    from jaeger_client import Config
    from flask_opentracing import FlaskTracing
    
    app = Flask(__name__)
    config = Config(
        config={
            'sampler':
            {'type': 'const',
             'param': 1},
                            'logging': True,
                            'reporter_batch_size': 1,}, 
                            service_name="pyserver")
    jaeger_tracer = config.initialize_tracer()
    tracing = FlaskTracing(jaeger_tracer, True, app)
    
    @app.route('/greet')
    def greet():
        return "Hello"
    ```
    
- In the Dockerfile: install required packages
    
    ```docker
    FROM alpine:3.14
    
    RUN apk add --no-cache py3-pip python3 && \
        pip3 install flask Flask-Opentracing jaeger-client
    
    COPY . /usr/src/pyserver
    
    ENV FLASK_APP app.py
    
    WORKDIR /usr/src/pyserver
    
    CMD flask run --host=0.0.0.0 --port=5000
    ```
    
- In the Kubernetes template: add annotations to make Jaeger agent as a sidecar
    
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: pyserver
      labels:
        name: pyserver
      annotations:
        "sidecar.jaegertracing.io/inject": "true"
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: pyserver
      template:
        metadata:
          labels:
            app: pyserver
        spec:
          containers:
            - name: pyserver
              image: lizhouyu/pyserver:v2
              imagePullPolicy: Always
              ports:
                - name: pyserver-port
                  containerPort: 5000
                  protocol: TCP
    ---
    apiVersion: v1
    kind: Service
    metadata:
        name: pyserver
    spec:
        selector:
            app: pyserver
        ports:
            - protocol: TCP
              port: 5000
              targetPort: 5000
    ```