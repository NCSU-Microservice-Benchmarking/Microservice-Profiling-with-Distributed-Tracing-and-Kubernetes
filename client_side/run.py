import argparse
from ast import arg
from curses import reset_prog_mode
from multiprocessing.connection import wait
from threading import Thread
from pyClient import VideoClient
from cassandra.cluster import Cluster
import pandas as pd
import time
import requests
import os
from tqdm import tqdm
import numpy as np

def detectVideo(args):
    video_client = VideoClient(video_path=args.video_path, frame_rate=args.frame_rate, jaeger_service_name=args.jaeger_service_name, jaeger_host_name=args.jaeger_host_name, jaeger_port=args.jaeger_port, service_host_name=args.service_host_name, service_port=args.service_port)
    video_client.detectVideo()

def main(NUM_GPU, NUM_CLIENTS, args):

    resp_config = requests.get('http://lin-res80.csc.ncsu.edu:8000/config?key=num_detectors&value='+str(NUM_GPU))
    if resp_config.status_code != 200:
        print("ERROR WHEN CHANGE NUM GPUs")
        return 1
    
    resp_resetMap = requests.get('http://lin-res80.csc.ncsu.edu:8000/resetMap')
    if resp_resetMap.status_code != 200:
        print("ERROR WHEN RESET CONFIG MAP")
        return 1    
    print("set num GPU: success!")
    if resp_resetMap.text != "success":
        print("UNABLE TO RESET MAP, WAIT AND TRY AGAIN")
        time.sleep(10)
        resp_resetMap = requests.get('http://lin-res80.csc.ncsu.edu:8000/resetMap')
        if resp_resetMap.text != "success":
            print("ERROR WHEN RESET CONFIG MAP")
            return 1    
    print("reset MAP: success!")
    
    time.sleep(2)

    cluster = Cluster(['lin-res80.csc.ncsu.edu'],port=8888)
    session = cluster.connect('jaeger_v1_dc1',wait_for_all_pools=True)
    session.execute('USE jaeger_v1_dc1')

    session.execute('TRUNCATE traces')
    print("clear database")

    time.sleep(2)

    threads = []

    for i in range(NUM_CLIENTS):
        thread_detect = Thread(target=detectVideo, args=(args,))
        thread_detect.start()
        threads.append(thread_detect)

    for t in threads:
        t.join(timeout=60)

    print("finish")
    time.sleep(30)

    list_num_gpu = []
    list_num_clients = []
    list_durations = []
    list_operation_names = []
    list_services = []
    rows = session.execute("select operation_name, process.service_name as service, duration from traces ALLOW filtering;")
    for row in rows:
        list_num_gpu.append(NUM_GPU)
        list_num_clients.append(NUM_CLIENTS)
        list_durations.append(int(row.duration))
        list_operation_names.append(row.operation_name)
        list_services.append(row.service)
    dataframe = pd.DataFrame({'Num GPU':list_num_gpu,'Num Client':list_num_clients, 'Operation Name': list_operation_names, 'Service': list_services, 'Duration': list_durations})
    if os.path.exists("data_points.csv"):
        dataframe.to_csv("data_points.csv",index=False,sep=',', mode='a',header=False)
    else:
        dataframe.to_csv("data_points.csv",index=False,sep=',', mode='w')
    print("data saved!")

    cluster.shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PyClient")
    parser.add_argument('--video_path', type=str, default='stuttgart_00.avi', help='path to the video file')
    parser.add_argument('--frame_rate', type=int, default=15, help='detection frame rate: for every <frame_rate> video frames, send one frame for detection')
    parser.add_argument('--jaeger_service_name', type=str, default="pyClient", help='jaeger tracing service name')
    parser.add_argument('--jaeger_host_name', type=str, default="lin-res80.csc.ncsu.edu", help='host name for jaeger tracing server')
    parser.add_argument('--jaeger_port', type=int, default=8009, help='port for jaeger tracing service')
    parser.add_argument('--jaeger_endpoint', type=str, default="http://lin-res80.csc.ncsu.edu:8009/api/traces", help='endpoint for jaeger tracing service')
    parser.add_argument('--service_host_name', type=str, default="lin-res80.csc.ncsu.edu", help='host name for object detection server')
    parser.add_argument('--service_port', type=int, default=8000, help='port for object detection service')
    args = parser.parse_args()

    # generate random shuffled list of number 1 to 7
    num_gpu_list = np.arange(1,8)
    num_client_list = np.array([10,20,30])
    np.random.shuffle(num_gpu_list)
    np.random.shuffle(num_client_list)

    # run experiment
    for NUM_GPU in num_gpu_list:
        for NUM_CLIENTS in num_client_list:
            main(NUM_GPU, NUM_CLIENTS, args)
            time.sleep(300)