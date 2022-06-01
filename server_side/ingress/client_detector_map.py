import time
import random

class ClientDetectorMap(object):
    def __init__(self, config):
        self.client_detecor_map = {} # {client id: detector port}
        self.detector_num_clients = {} # {detecor port: number of serving clients}
        self.client_last_request_time = {} # {client id: lastest times(second) of client's request}
        self.ttl = int(config['ttl'])
        self.num_detectors = int(config['num_detectors'])
        self.detector_ports = config['detector_ports'].split(',')[0:self.num_detectors]
        self.max_num_clients = int(config['max_num_clients'])

        # initial the detector_num_clients map
        for detector_port in self.detector_ports:
            self.detector_num_clients[detector_port] = 0

    # generate client id    
    def genClientId(self):
        while True:
            client_id = str(random.randint(0, self.max_num_clients))
            if client_id not in self.client_detecor_map:
                self.addClient(client_id)
                break
            if len(self.client_detecor_map) >= self.max_num_clients:
                client_id = -1
                break
        return client_id

    def addClient(self, client_id):
        # if client already in the map, update last request time and return its assigned detector port
        if client_id in self.client_detecor_map:
            self.client_last_request_time[client_id] = int(time.time())
            return self.client_detecor_map[client_id]
        # get the detector port with min assigned client
        assigned_port = min(self.detector_num_clients, key=self.detector_num_clients.get)
        # assign the port to the given client
        self.client_detecor_map[client_id] = assigned_port
        # the assigned port's serving clients +1
        self.detector_num_clients[assigned_port] += 1
        # clinet's last request time is current time
        self.client_last_request_time[client_id] = int(time.time())
        # return the assigned port
        return assigned_port
    
    def getPort(self, client_id):
        # if the client is not assigned, return unauthorized user # assign it
        if client_id not in self.client_detecor_map:
            return "unauthorized user"
            #return self.addClient(client_id)
        # otherwise, update last request time and get the client's assigned port
        self.client_last_request_time[client_id] = int(time.time())
        return self.client_detecor_map[client_id]
    
    def updateClientLastRequestTime(self, client_id):
        self.client_last_request_time[client_id] = int(time.time())
        return True
    
    def getAllClientIds(self):
        client_id_list = []
        for client_id in self.client_detecor_map.keys():
            client_id_list.append(client_id)
        return client_id_list
    
    def relaeseResource(self):
        current_time = int(time.time())
        nonactive_clients = []
        for client_id, last_request_time in self.client_last_request_time.items():
            if last_request_time + self.ttl < current_time:
                nonactive_clients.append(client_id)

        # delete nonactive clients
        for client_id in nonactive_clients:
            detector_port = self.client_detecor_map[client_id]
            self.client_detecor_map.pop(client_id)
            self.client_last_request_time.pop(client_id)
            self.detector_num_clients[detector_port] -= 1

    def relaeseClinetResource(self, client_id):
        detector_port = self.client_detecor_map[client_id]
        self.client_detecor_map.pop(client_id)
        self.client_last_request_time.pop(client_id)
        self.detector_num_clients[detector_port] -= 1
        return True

    # reset map with new config when the map is empty
    # returns:
    #   0: reset success
    #   1: map not empty
    def reset(self, config): 
        if len(self.client_detecor_map) > 0:
            return 1
        self.client_detecor_map = {} # {client id: detector port}
        self.detector_num_clients = {} # {detecor port: number of serving clients}
        self.client_last_request_time = {} # {client id: lastest times(second) of client's request}
        self.ttl = int(config['ttl'])
        self.num_detectors = int(config['num_detectors'])
        self.detector_ports = config['detector_ports'].split(',')[0:self.num_detectors]
        # initial the detector_num_clients map
        for detector_port in self.detector_ports:
            self.detector_num_clients[detector_port] = 0
        return 0


