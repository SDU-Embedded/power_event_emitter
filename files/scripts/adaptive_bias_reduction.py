#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys

class BiasFilter():
    # Saves samples in buffer of length 'buffer_size'
    # Calculates new average every 'estimate_freq' samples
    def __init__(self, buffer_size, estimate_freq, initial_bias):
       
        # Save variables
        self.buffer_size = buffer_size
        self.estimate_freq = estimate_freq
        
        self.values = [0.0]*self.buffer_size
        self.pointer = 0
        self.bias = initial_bias
        self.sample_counter = 0

    def step(self, value):
        # Insert new value in buffer
        self.values[self.pointer] = value
        
        # Increment buffer pointer and handle overflow
        self.pointer = self.pointer + 1
        if self.pointer == self.buffer_size:
            self.pointer = 0

        # Check if it is time to recalculate bias
        self.sample_counter = self.sample_counter + 1
        if self.sample_counter > self.estimate_freq:
            self.sample_counter = 0
            self.bias = sum(self.values)/self.buffer_size

        return value - self.bias



if __name__ == "__main__":
    filter = BiasFilter( int(sys.argv[1]),  int(sys.argv[2], int(sys.argv[3]) )

    try:
        while True:
            line = sys.stdin.readline().rstrip()
            #print (line)
            if line:
                print filter.step(float(line))
    except KeyboardInterrupt:
        sys.stdout.flush()
        pass


