#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#

import os,time,sys,json,copy
from datetime import datetime
from kafka import KafkaProducer
from distutils import util

class EventParser():
    def __init__(self):
        self.event = dict()
        self.contents = dict()
        self.contents["id"] = int(sys.argv[1])
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
            #self.event = copy.deepcopy(self.last_onset_event)
            self.event["@timestamp"] = datetime.utcnow()
            self.event["data"]["event"] = dat
            self.event["data"]["duration"] = duration
            self.emit_event()

class EventEmitter():
    def __init__(self, servers, topic):
        self.servers = servers
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=self.servers)

    def send(self, dat):
        #print (dat)
        self.producer.send(self.topic, dat.encode())

class Thresholder():
    def __init__(self):
        # Init state parser
        self.event_parser = EventParser()
        
        # State variables
        self.on = False
        self.line_counter = 0

        # Init parameters
        self.parameters = dict()
        self.parameter_file = 'parameters.json'
        self.read_parameters()
        
        # Variables for filter 
        self.pointer = 0
        self.values = [5.0]*100 # Max filter size is 100

        # Other class variables

    def read_parameters(self):
        try:
            with open(self.parameter_file) as myfile:
                self.parameters = json.loads( list(myfile)[-1] )
        except:
            # Handle as initial run (there is no file)
            self.parameters['time'] = datetime.utcnow().isoformat()
            self.parameters['max'] = 0.0
            self.parameters['min'] = 100.0
            self.parameters['upwards_threshold'] = float(sys.argv[3])
            self.parameters['downwards_threshold'] = float(sys.argv[4])
            self.parameters['filter_size'] = int(sys.argv[6])
            self.parameters['event_on_high'] = bool(util.strtobool(sys.argv[5]))
            file_handle = open(self.parameter_file, "w")
            file_handle.write( json.dumps(self.parameters) + '\n')
            file_handle.close()

    def write_parameters(self):
        try:
            self.parameters['time'] = datetime.utcnow().isoformat()
            file_handle = open(self.parameter_file, "a")
            file_handle.write( json.dumps(self.parameters) + '\n')
            file_handle.close()
        except:
            pass


    def evaluate(self, value):
    # Called for each line received
        
        # Insert new value in buffer
        self.values[self.pointer] = float(value)

        # Increment buffer pointer and handle overflow
        self.poiner = self.pointer + 1
        if self.pointer > self.parameters['filter_size']:
            self.pointer = 0

        # Calculate average of buffer
        average = sum(self.values[0:self.parameters['filter_size']])/self.parameters['filter_size']
        #print (average)

        # Keep track of the maximum value so far
        if average > self.parameters['max']:
            self.parameters['max'] = average
            self.write_parameters()
            #print ("  New max:" + str(average) + " Up:" + str(self.parameters['upwards_threshold']) + " Down:" + str(self.parameters['downwards_threshold']))
        
        # Keep track of the minimum value so far
        if average < self.parameters['min']:
            self.parameters['min'] = average
            self.write_parameters()
            #print ("  New min:" + str(average) + " Up:" + str(self.parameters['upwards_threshold']) + " Down:" + str(self.parameters['downwards_threshold']))

        # Evaluate state
        if self.parameters['event_on_high']:
            if self.on:
                if average < self.parameters['downwards_threshold']:
                    self.on = False
                    #print ("  Offset event")
                    self.event_parser.evaluate('offset')
            else:
                if average > self.parameters['upwards_threshold']:
                    self.on = True
                    #print ("  Onset event")
                    self.event_parser.evaluate('onset')
        else:
            if self.on:
                if average > self.parameters['upwards_threshold']:
                    self.on = False
                    #print ("  Offset event")
                    self.event_parser.evaluate('offset')
            else:
                if average < self.parameters['downwards_threshold']:
                    self.on = True
                    #print ("  Onset event")
                    self.event_parser.evaluate('onset')
        
        # Reload values for every 100 lines in case they were changed
        self.line_counter = self.line_counter + 1
        if self.line_counter == 100:
            self.line_counter = 0
            self.read_parameters()

if __name__ == "__main__":
    thresholder = Thresholder()

    try:
        while True:
            line = sys.stdin.readline().rstrip()
            #print (line)
            if line:
                print (line)
                thresholder.evaluate(float(line))
                
                #try:
                #    print (line)
                #    sys.stdout.flush()
                #except (UnicodeEncodeError, ValueError) as e:
                #    pass
    except KeyboardInterrupt:
        sys.stdout.flush()
        pass


