import json
import numpy as np
import requests
from flask_apscheduler import APScheduler

from flask import request
from flask import Flask
from flask import Response
from flask import jsonify

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace import set_span_in_context

from client_detector_map import ClientDetectorMap

# config dict, key and value are all strings, convert to desired data type when using 
config = {
    'jaeger_service_name': "pyServer-ingress",
    'jaeger_agent_host_name': 'localhost',
    'jaeger_agent_port': '6831',
    'jaeger_collector_endpoint': 'http://lin-res80.csc.ncsu.edu:8009/api/traces',
    'max_num_clients': '100',
    'num_detectors': '7',
    'detector_host_name': 'localhost',
    'detector_ports': '8001,8002,8003,8004,8005,8006,8007',
    'ttl': '10' # seconds to evict nonactive clients
}

class FlaskConfig(object):
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()

app = Flask(__name__)
app.config.from_object(FlaskConfig())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def initJaegerTracer(service_name, agent_host_name, agent_port, collector_endpoint):
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })

    jaeger_exporter = JaegerExporter(
        agent_host_name=agent_host_name,
        agent_port=int(agent_port),
        collector_endpoint= collector_endpoint #'http://eb2-2259-lin04.csc.ncsu.edu:14269/api/traces',
    )

    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer(__name__)

    return tracer


tracer = initJaegerTracer(service_name=config['jaeger_service_name'], agent_host_name=config['jaeger_agent_host_name'], agent_port=config['jaeger_agent_port'], collector_endpoint=config['jaeger_collector_endpoint'])

client_detector_map = ClientDetectorMap(config=config)

@scheduler.task('interval', id='release_resource', seconds=int(config['ttl']), misfire_grace_time=900)
def releaseResource():
    client_detector_map.relaeseResource()

@app.route('/greet')
def greet():
    context = TraceContextTextMapPropagator().extract(carrier=request.headers)
    with tracer.start_span(name='greet_server_span', context=context) as greet_server_span:
        return("Hello")

# modify the configuration
@app.route('/config')
def changeConfig():
    key = request.args.get('key')
    value = request.args.get('value')
    if key in config:
        config[key] = value
    return jsonify(config)

# reset the map with new config
@app.route('/resetMap')
def resetMap():
    feedback_value = client_detector_map.reset(config)
    message = ""
    if feedback_value == 0:
        message = "success"
    elif feedback_value == 1:
        message = "map is not empty, please try again later"
    else:
        message = "unknown error"
    return message

# reset the Jaeger Exporter with new config
@app.route('/resetJaeger')
def resetJaeger():
    tracer = initJaegerTracer(service_name=config['jaeger_service_name'], agent_host_name=config['jaeger_agent_host_name'], agent_port=config['jaeger_agent_port'], collector_endpoint=config['jaeger_collector_endpoint'])
    return "success"

# get client id
@app.route('/getId')
def getClientId():
    context = TraceContextTextMapPropagator().extract(carrier=request.headers)
    with tracer.start_as_current_span(name='generate_client_id', context=context) as gen_id_span:
        client_id = client_detector_map.genClientId()
        resp_headers = {}
        TraceContextTextMapPropagator().inject(resp_headers)
        return str(client_id), resp_headers

@app.route('/getPort')
def getPort():
    context = TraceContextTextMapPropagator().extract(carrier=request.headers)
    with tracer.start_as_current_span(name='get_detector_port', context=context) as gen_id_span:
        client_id = json.loads(request.get_data())['client_id']
        detector_port = client_detector_map.getPort(client_id)
        resp_headers = {}
        TraceContextTextMapPropagator().inject(resp_headers)
        return str(detector_port), resp_headers

@app.route('/ping')
def pingServer():
    context = TraceContextTextMapPropagator().extract(carrier=request.headers)
    with tracer.start_as_current_span(name='get_ping_from_client', context=context) as gen_id_span:
        client_id = json.loads(request.get_data())['client_id']
        client_detector_map.updateClientLastRequestTime(client_id)
        resp_headers = {}
        TraceContextTextMapPropagator().inject(resp_headers)
        return str("done"), resp_headers

@app.route('/releaseClient')
def releaseClinet():
    context = TraceContextTextMapPropagator().extract(carrier=request.headers)
    with tracer.start_as_current_span(name='release_client_connection', context=context) as gen_id_span:
        client_id = json.loads(request.get_data())['client_id']
        client_detector_map.relaeseClinetResource(client_id)
        resp_headers = {}
        TraceContextTextMapPropagator().inject(resp_headers)
        return str("done"), resp_headers

@app.route('/detect',methods=['GET','POST'])
def detect():
    context = TraceContextTextMapPropagator().extract(carrier=request.headers)
    with tracer.start_as_current_span(name='ingress', context=context) as ingress_span:
        # check client_id and get port
        req_data = request.get_data()
        dict_req_data = json.loads(req_data)
        client_id = dict_req_data['client_id']
        detector_port = client_detector_map.getPort(client_id)
        if detector_port == "unauthroized user":
            resp_headers = {}
            TraceContextTextMapPropagator().inject(resp_headers)
            return "unauthroized user, please apply for a client id", resp_headers
        # once get a valid port, retrieve the frame from request and forward it to the assigned detector
        forward_headers = {"content-type":"image/jpg"}
        forward_data = dict_req_data['image']
        TraceContextTextMapPropagator().inject(forward_headers)
        resp = requests.post(url='http://'+config['detector_host_name']+':'+detector_port+'/detect', headers=forward_headers, data=forward_data)
        # once received detection result, send the result back to the client
        context_from_detector = TraceContextTextMapPropagator().extract(carrier=resp.headers)
        with tracer.start_as_current_span(name='response', context=context_from_detector) as response_span:
            resp_headers = {}
            TraceContextTextMapPropagator().inject(resp_headers)
            return resp.text, resp_headers