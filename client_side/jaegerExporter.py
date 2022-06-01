from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

class JaegerTracer(object):
    def __init__(self, service_name, host_name, port):
        trace.set_tracer_provider(
        TracerProvider(
                resource=Resource.create({SERVICE_NAME: service_name})
            )
        )
        self.tracer = trace.get_tracer(__name__)

        # create a JaegerExporter
        jaeger_exporter = JaegerExporter(
            # configure agent
            agent_host_name= host_name, #'eb2-2259-lin04.csc.ncsu.edu',
            agent_port= 6831, #14269,
            # optional: configure also collector
            collector_endpoint= 'http://'+host_name+':'+str(port)+'/api/traces' #'http://eb2-2259-lin04.csc.ncsu.edu:14269/api/traces',
            # username=xxxx, # optional
            # password=xxxx, # optional
            # max_tag_value_length=None # optional
        )

        # Create a BatchSpanProcessor and add the exporter to it
        span_processor = BatchSpanProcessor(jaeger_exporter)
        #span_processor = BatchSpanProcessor(ConsoleSpanExporter())

        # add to the tracer
        trace.get_tracer_provider().add_span_processor(span_processor)
    
    def getTracer(self):
        return self.tracer


if __name__ == "__main__":
    jaegerTracer = JaegerTracer("pyClient", 'eb2-2259-lin04.csc.ncsu.edu', 14269, 'http://eb2-2259-lin04.csc.ncsu.edu:14269/api/traces')
    with jaegerTracer.getTracer().start_as_current_span('python-client-hello'):
        print('Hello world!')