#!/usr/bin/env python

import os,time,sys,json,copy
from datetime import datetime

size = 10
values = [5.0]*size
pointer = 0
max_average = 0.0
min_average = 5.0
upwards_threshold_percent = 30.0
downwards_threshold_percent = 20.0
upwards_threshold = 0.0
downwards_threshold = 0.0
on = False

try:
    while True:
        line = sys.stdin.readline().rstrip()
        
        values[pointer] = float(line)
        
        poiner = pointer + 1
        if pointer > size:
            pointer = 0

        average = sum(values)/size
        print average

        if average > max_average:
            max_average = average
            upwards_threshold = ((average - min_average)*upwards_threshold_percent/100.0)+min_average
            downwards_threshold = ((average - min_average)*downwards_threshold_percent/100.0)+min_average
            print "  New max:" + str(average) + " Up:" + str(upwards_threshold) + " Down:" + str(downwards_threshold)
        if average < min_average:
            min_average = average
            upwards_threshold = ((average - min_average)*upwards_threshold_percent/100.0)+min_average
            downwards_threshold = ((average - min_average)*downwards_threshold_percent/100.0)+min_average
            print "  New min:" + str(average) + " Up:" + str(upwards_threshold) + " Down:" + str(downwards_threshold)

        if on: 
            if average < downwards_threshold:
                on = False
                print "  Offset event"
        else:
            if average > upwards_threshold:
                on = True
                print "  Onset event"

except KeyboardInterrupt:
    sys.stdout.flush()
    pass

