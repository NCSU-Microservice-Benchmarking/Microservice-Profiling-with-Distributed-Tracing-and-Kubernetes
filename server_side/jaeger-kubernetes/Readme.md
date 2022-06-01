# Setup **Cassandra Backing storage**

The Jaeger Collector and Query require a backing storage to exist before being started up. As a starting point for your own templates, we provide basic templates deploying Cassandra and Elasticsearch. None of them are ready for production and should be adapted before any real usage.

To use our Cassandra template:

1. install configmap  
    ```cpp
    kubectl create -f configmap.yml
    ```
    if local file does not exist:

    ```cpp
    kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-kubernetes/master/production/configmap.yml
    ```

2. install Cassandra
    ```cpp
    kubectl create -f cassandra.yml
    ```

    The Cassandra template includes also a Kubernetes Job that creates the schema required by the Jaeger components. It's advisable to wait for this job to finish before deploying the Jaeger components.  

3. To check the status of the job, run:

    ```cpp
    kubectl get job jaeger-cassandra-schema-job
    ```

    The job should have 1 in the SUCCESSFUL column.

# Set up Jaeger with Jaeger Operator

## Install pre-requisites

1. [Deploy ingress (Nginx)](https://kubernetes.github.io/ingress-nginx/deploy/#quick-start)
    
    ```bash
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.2.0/deploy/static/provider/cloud/deploy.yaml
    ```
    
2. [Install cert-manager](https://cert-manager.io/docs/installation/kubectl/)
    
    ```bash
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.8.0/cert-manager.yaml
    ```
    

## Install Jaeger Operator

Following [the latest tutorial](https://www.jaegertracing.io/docs/1.33/operator/#installing-the-operator-on-kubernetes) to install Jaeger Operator

```bash
kubectl create namespace observability # <1>
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.33.0/jaeger-operator.yaml -n observability # <2>
```

## Deploy Jaeger with Cassandra using Jaeger Operator

1. Create a template file named `deploy_jaeger_cassandra.yaml` with following content
    
    ```yaml
    apiVersion: jaegertracing.io/v1
    kind: Jaeger
    metadata:
      name: simple-prod
    spec:
      strategy: production
      collector:
        maxReplicas: 5
        resources:
          limits:
            cpu: 100m
            memory: 128Mi
      storage:
        type: cassandra
        options:
          cassandra:
            servers: cassandra
            keyspace: jaeger_v1_datacenter
        cassandraCreateSchema:
          datacenter: "datacenter"
          mode: "test"
    ```
    
2. Deploy jaeger
    
    ```bash
    kubectl apply -f deploy_jaeger_cassandra.yaml
    ```
    
3. Set port-forward for Jaeger Query
    
    ```bash
    kubectl port-forward --address 0.0.0.0 svc/simple-prod-query 16686:16686
    ```
    
    Then the Jaeger UI can be visited at: server-ip:16686
    
4. Set port-forward for Jaeger Collector
    
    ```bash
    kubectl port-forward --address 0.0.0.0 svc/simple-prod-collector 14268:14268
    ```