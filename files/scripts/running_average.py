#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys

class AverageFilter():
    def __init__(self, size):
        self.size = size
        self.values = [0.0]*self.size
        self.pointer = 0

    def step(self, value):
        # Insert new value in buffer
        self.values[self.pointer] = float(value)

        # Increment buffer pointer and handle overflow
        self.poiner = self.pointer + 1
        if self.pointer > self.size:
            self.pointer = 0

        return self.calculate()

    def calculate(self):
        # Calculate average of buffer
        average = sum(self.values)/self.size
        
        return average


if __name__ == "__main__":
    filter = AverageFilter( int(sys.argv[1]) )

    try:
        while True:
            line = sys.stdin.readline().rstrip()
            #print (line)
            if line:
                print filter.step(float(line))
    except KeyboardInterrupt:
        sys.stdout.flush()
        pass


