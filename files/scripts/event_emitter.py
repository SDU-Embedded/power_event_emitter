#!/usr/bin/env python
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
        self.event_emitter = EventEmitter('manna,hou,bisnap','power')

    def get_time_since_last_event(self):
        current_time = datetime.utcnow()
        previous_time = self.event["@timestamp"]
        return (current_time - previous_time).total_seconds()
    
    def emit_event(self):
        tmp = copy.deepcopy(self.event)
        tmp["@timestamp"] = self.event["@timestamp"].isoformat()
        self.event_emitter.send( json.dumps(tmp) )

    def evaluate(self, dat):
        if 'onset' in self.event:
            self.event["@timestamp"] = datetime.utcnow()
            self.event["data"]["event"] = dat
            self.event["data"]["duration"] = 0.0
            self.last_onset_event = copy.deepcopy(self.event)
            emit_event()
        else:
            duration = get_time_since_last_event()
            self.event = copy.deepcopy(last_onset_event)
            self.event["data"]["event"] = dat
            self.event["data"]["duration"] = duration
            emit_event()

class EventEmitter():
    def __init__(self, servers, topic):
        self.servers = servers
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=self.servers) 

    def send(self, dat):
        self.producer.send(self.topic, dat)

class Thresholder():
    def __init__(self):
        self.size = 10
        self.values = [5.0]*size
        self.pointer = 0
        self.max_average = 0.0
        self.min_average = 5.0
        self.upwards_threshold_percent = 30.0
        self.downwards_threshold_percent = 20.0
        self.upwards_threshold = 0.0
        self.downwards_threshold = 0.0
        self.on = False
        self.event_parser = EventParser()

    def evaluate(self, value):
        self.values[pointer] = float(value)

        self.poiner = self.pointer + 1
        if self.pointer > self.size:
            self.pointer = 0

        average = sum(self.values)/self.size
        #print average
        
        if average > self.max_average:
            self.max_average = average
            self.upwards_threshold = ((average - self.min_average)*self.upwards_threshold_percent/100.0)+self.min_average
            self.downwards_threshold = ((average - self.min_average)*self.downwards_threshold_percent/100.0)+self.min_average
            #print "  New max:" + str(average) + " Up:" + str(self.upwards_threshold) + " Down:" + str(self.downwards_threshold)
        if average < min_average:
            self.min_average = average
            self.upwards_threshold = ((average - self.min_average)*self.upwards_threshold_percent/100.0)+self.min_average
            self.downwards_threshold = ((average - self.min_average)*self.downwards_threshold_percent/100.0)+self.min_average
            #print "  New min:" + str(average) + " Up:" + str(self.upwards_threshold) + " Down:" + str(self.downwards_threshold)

        if self.on:
            if average < self.downwards_threshold:
                self.on = False
                self.event_parser.evaluate('offset')
                #print "  Offset event"
        else:
            if average > self.upwards_threshold:
                self.on = True
                self.event_parser.evaluate('onset')
                #print "  Onset event"

if __name__ == "__main__":
    thresholder = Thresholder()

    try:
        while True:
            line = sys.stdin.readline().rstrip()
            thresholder.evaluate(float(line))
    except KeyboardInterrupt:
        sys.stdout.flush()
        pass


