from turtle import mode
import cv2
import base64
import json
import torch
import numpy as np
from flask import request
from flask import Flask
from flask import Response
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace import set_span_in_context

app = Flask(__name__)

resource = Resource(attributes={
    SERVICE_NAME: "pyServer"
})

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
    collector_endpoint= 'http://lin-res80.csc.ncsu.edu:8009/api/traces' #'http://eb2-2259-lin04.csc.ncsu.edu:14269/api/traces',
)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# initial the model
model = torch.hub.load('yolov5', 'yolov5s', pretrained=True, source='local')
model.eval()

@app.route('/greet')
def greet():
    context = TraceContextTextMapPropagator().extract(carrier=request.headers)
    with tracer.start_span(name='greet_server_span', context=context) as greet_server_span:
        return("Hello")

@app.route('/count_gpu')
def countGPU():
        return str(torch.cuda.device_count())

@app.route('/detect',methods=['GET','POST'])
def detect():
    context = TraceContextTextMapPropagator().extract(carrier=request.headers)
    with tracer.start_as_current_span(name='detect', context=context) as detect_server_span:
        # get base64 jpg image data from request data, and restore it to the jpg image
        jpg_original = base64.b64decode(request.data)
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        frame = cv2.imdecode(jpg_as_np, flags=1)
        # run object detection
        results = model(frame)
        # send result back to the ingress server
        resp_headers = {}
        TraceContextTextMapPropagator().inject(resp_headers)
        return results.pandas().xyxy[0].to_json(orient="records"), resp_headers



    