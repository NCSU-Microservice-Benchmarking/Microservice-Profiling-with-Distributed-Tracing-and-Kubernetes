import cv2
import time
import json
import base64
from queue import Queue
import socket
import logging
import requests
from threading import Thread
from opentelemetry.trace import set_span_in_context
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from jaegerExporter import JaegerTracer
from videoReader import VideoReader
from utils import getMyLogger


class VideoClient(object):
    def __init__(self, video_path="", frame_rate=15, jaeger_service_name="pyClient", jaeger_host_name="lin-res80.csc.ncsu.edu", jaeger_port=8009, service_host_name="lin-res80.csc.ncsu.edu", service_port=8000):
        self.jaeger_tracer = JaegerTracer(jaeger_service_name, jaeger_host_name, jaeger_port)
        self.video_reader = VideoReader(video_path)
        self.frame_rate = 2*self.video_reader.getFPS()
        
        self.service_host_name = service_host_name
        self.service_port = service_port
        self.service_socket = service_host_name + ':' + str(service_port)
        self.client_id = ""
        self.client_port = ""
        self.detection_socket = ""
        self.detection_results = {} # dict to store detection results, {frame_number: frame_detection_result}

    def greet(self):
        with self.jaeger_tracer.getTracer().start_as_current_span('python-CS-test_' + str(int(time.time()*1000))) as parent_span:
            headers = {}
            TraceContextTextMapPropagator().inject(headers)
            requests.get(url='http://'+self.service_socket+'/greet', headers=headers)
        
    def detectFrame(self, frame, frame_count, span_context):
        with self.jaeger_tracer.getTracer().start_as_current_span(name='frame '+str(frame_count)+' detection', context=span_context):
            print('detecting ', frame_count, ' frame')
            # with self.jaeger_tracer.getTracer().start_as_current_span('frame_object_detect' + str(int(time.time()*1000))) as parent_span:
            # data = {'image':cv2.imencode('.jpg', frame)[1].tobytes(), 'client_id':self.client_id}
            retval, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            data = jpg_as_text
            # data = {'image':jpg_as_text, 'client_id':self.client_id}
            #headers = {"content-type":"image/jpg"} #'Content-Type': 'application/json'
            with self.jaeger_tracer.getTracer().start_as_current_span(name='frame '+str(frame_count)+' send to server for detection'):
                headers = {"content-type":"image/jpg"} # headers = {'Content-Type': 'application/json'}
                TraceContextTextMapPropagator().inject(headers)
                resp = requests.post(url='http://'+self.detection_socket+'/detect', headers=headers, data=data)
                context_from_server = TraceContextTextMapPropagator().extract(carrier=resp.headers)
                with self.jaeger_tracer.getTracer().start_as_current_span(name='frame '+str(frame_count)+' ping server and post detection process', context=context_from_server):
                    if resp.status_code == 200:
                        self.detection_results[frame_count] = resp.text
                    else:
                        self.detection_results[frame_count] = 'Error: '+str(resp.status_code)
                    # resp = requests.get(url='http://'+self.service_socket+'/ping', data=json.dumps({'client_id': self.client_id}))
                    print('frame', frame_count, ' detected')

    def detectVideo(self):
        threads = []
        with self.jaeger_tracer.getTracer().start_as_current_span('video_detection') as video_detection_span:
            with self.jaeger_tracer.getTracer().start_as_current_span("request_id"):
                headers = {} #'Content-Type': 'application/json'
                TraceContextTextMapPropagator().inject(headers)
                resp_id = requests.get(url='http://'+self.service_socket+'/getId', headers=headers)
                self.client_id = resp_id.text
                print(self.client_id)
                server_context_get_id = TraceContextTextMapPropagator().extract(carrier=resp_id.headers)
                with self.jaeger_tracer.getTracer().start_as_current_span("request_port", context=server_context_get_id):
                    resp_port = requests.get(url='http://'+self.service_socket+'/getPort', headers=headers, data=json.dumps({'client_id': self.client_id}))
                    self.client_port = resp_port.text
                    self.detection_socket = self.service_host_name + ':' + self.client_port
                    server_context_get_port = TraceContextTextMapPropagator().extract(carrier=resp_port.headers)
                    with self.jaeger_tracer.getTracer().start_as_current_span("start_detection", context=server_context_get_port):
                        while True:
                            flag, frame, frame_byte_array = self.video_reader.readNextFrame()
                            frame_count = self.video_reader.getFramesCount()
                            if flag == False:
                                if self.video_reader.is_finish_playing():
                                    break
                                else:
                                    continue
                            if frame_count % self.frame_rate == 0:
                                span_context = set_span_in_context(video_detection_span)
                                thread_detect = Thread(target=self.detectFrame, args=(frame, frame_count, span_context))
                                thread_detect.start()
                                threads.append(thread_detect)
                        for t in threads:
                            t.join()
                        self.video_reader.releaseVideo()
                        print(self.detection_results)
                        # with self.jaeger_tracer.getTracer().start_as_current_span("release_resource"):
                        #     resp = requests.get(url='http://'+self.service_socket+'/releaseClient', data=json.dumps({'client_id': self.client_id}))
                        #     print("release reource for client", self.client_id, resp.text)


# TODO: Implement Camera Client

        

if __name__ == "__main__":

    video_client = VideoClient('stuttgart_00.avi',service_host_name="lin-res80.csc.ncsu.edu")