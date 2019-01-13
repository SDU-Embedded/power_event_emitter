#!/usr/bin/env python

import os,time,sys,json,copy
from datetime import datetime

event = dict()
contents = dict()
contents["bird"] = int(sys.argv[1])
contents["type"] = str(sys.argv[2])
contents["duration"] = 0.0
event["data"] = contents
event["@timestamp"] = datetime.utcnow()
last_onset_event = copy.deepcopy(event)

def get_time_since_last_event():
    current_time = datetime.utcnow()
    previous_time = event["@timestamp"]
    return (current_time - previous_time).total_seconds()

def emit_event():
    tmp = copy.deepcopy(event)
    tmp["@timestamp"] = event["@timestamp"].isoformat()
    print json.dumps(tmp)

try:
    while True:
        line = sys.stdin.readline().rstrip()
        if 'onset' in line:
            event["@timestamp"] = datetime.utcnow()
            event["data"]["event"] = line
            event["data"]["duration"] = 0.0
            #sha_command = "echo \"" + str(event) + "\" | sha1sum | cut -d' ' -f1"
            #event["hash"] = os.popen(sha_command).read().rstrip()
            last_onset_event = copy.deepcopy(event)
            emit_event()
        else:
            duration = get_time_since_last_event()
            event = copy.deepcopy(last_onset_event)
            event["data"]["event"] = line
            event["data"]["duration"] = duration
            emit_event()

except KeyboardInterrupt:
    sys.stdout.flush()
    pass

