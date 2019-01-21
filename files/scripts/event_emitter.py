#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import os,time,sys,json,copy
from datetime import datetime
from kafka import KafkaProducer

class EventParser():
    def __init__(self):
        self.event = dict()
        self.contents = dict()
        self.contents["bird"] = int(sys.argv[1])
        self.contents["type"] = str(sys.argv[2])
        self.contents["duration"] = 0.0
        self.event["data"] = self.contents
        self.event["@timestamp"] = datetime.utcnow()
        self.last_onset_event = copy.deepcopy(self.event)
        self.event_emitter = EventEmitter('manna,hou,bisnap',str(sys.argv[2]))

    def get_time_since_last_event(self):
        current_time = datetime.utcnow()
        previous_time = self.event["@timestamp"]
        return (current_time - previous_time).total_seconds()

    def emit_event(self):
        tmp = copy.deepcopy(self.event)
        tmp["@timestamp"] = self.event["@timestamp"].isoformat()
        self.event_emitter.send( json.dumps(tmp) )

    def evaluate(self, dat):
        if 'onset' in dat:
            self.event["@timestamp"] = datetime.utcnow()
            self.event["data"]["event"] = dat
            self.event["data"]["duration"] = 0.0
            self.last_onset_event = copy.deepcopy(self.event)
            self.emit_event()
        else:
            duration = self.get_time_since_last_event()
            self.event = copy.deepcopy(self.last_onset_event)
            self.event["data"]["event"] = dat
            self.event["data"]["duration"] = duration
            self.emit_event()

class EventEmitter():
    def __init__(self, servers, topic):
        self.servers = servers
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=self.servers)

    def send(self, dat):
        print (dat)
        self.producer.send(self.topic, dat.encode())

class Thresholder():
    def __init__(self):
        self.event_on_high = True
        self.size = 10
        self.values = [5.0]*self.size
        self.pointer = 0
        self.upwards_threshold_percent = float(sys.argv[3]) # 30.0
        self.downwards_threshold_percent = float(sys.argv[4]) # 20.0
        self.upwards_threshold = 0.0
        self.downwards_threshold = 0.0
        self.on = False
        self.event_parser = EventParser()

        self.parameters = dict()

        self.parameter_file = 'parameters.json'

        try:
            with open(self.parameter_file) as myfile:
                self.parameters = json.loads( list(myfile)[-1] )
        except:
            self.parameters['time'] = datetime.utcnow().isoformat()
            self.parameters['max'] = 0.0
            self.parameters['min'] = 100.0
            file_handle = open(self.parameter_file, "w")
            file_handle.write( json.dumps(self.parameters) + '\n')
            file_handle.close()

    def evaluate_thresholds(self,average):
        self.upwards_threshold = ((average - self.parameters['min'])*self.upwards_threshold_percent/100.0)+self.parameters['min']
        self.downwards_threshold = ((average - self.parameters['min'])*self.downwards_threshold_percent/100.0)+self.parameters['min']
        self.parameters['time'] = datetime.utcnow().isoformat()
        file_handle = open(self.parameter_file, "a")
        file_handle.write( json.dumps(self.parameters) + '\n')
        file_handle.close()

    def evaluate(self, value):
        self.values[self.pointer] = float(value)

        self.poiner = self.pointer + 1
        if self.pointer > self.size:
            self.pointer = 0

        average = sum(self.values)/self.size
        #print (average)

        if average > self.parameters['max']:
            self.parameters['max'] = average
            self.evaluate_thresholds(average)
            #print ("  New max:" + str(average) + " Up:" + str(self.upwards_threshold) + " Down:" + str(self.downwards_threshold))
        if average < self.parameters['min']:
            self.parameters['min'] = average
            self.evaluate_thresholds(average)
            #print ("  New min:" + str(average) + " Up:" + str(self.upwards_threshold) + " Down:" + str(self.downwards_threshold))

        if self.event_on_high:
            if self.on:
                if average < self.downwards_threshold:
                    self.on = False
                    #print ("  Offset event")
                    self.event_parser.evaluate('offset')
            else:
                if average > self.upwards_threshold:
                    self.on = True
                    #print ("  Onset event")
                    self.event_parser.evaluate('onset')
        else:
            if self.on:
                if average > self.upwards_threshold:
                    self.on = False
                    #print ("  Offset event")
                    self.event_parser.evaluate('offset')
            else:
                if average < self.downwards_threshold:
                    self.on = True
                    #print ("  Onset event")
                    self.event_parser.evaluate('onset')

if __name__ == "__main__":
    thresholder = Thresholder()

    try:
        while True:
            line = sys.stdin.readline().rstrip()
            #print (line)
            if line:
                thresholder.evaluate(float(line))
    except KeyboardInterrupt:
        sys.stdout.flush()
        pass


