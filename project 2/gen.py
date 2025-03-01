import math
import rand
from copy import deepcopy

class rand48:
    def __init__(self, seed):
        self.a = 0x5DEECE66D
        self.b = 0xB
        self.x_1 = bin(0x330E)[2:].zfill(16)
        self.x_2 = bin(seed)[2:].zfill(32)
        self.x = int(self.x_1+self.x_2, 2)
        self.y = 2**48

    def get_next(self):
        self.x = (self.a*self.x + self.b) & (self.y - 1)
        return self.x
    
    def drand48(self):
        return self.get_next()/self.y
    
class Process(object):
    def __init__(self, arrival_time, cpu_bursts, intervals, io_process):
        self.arrival_time = arrival_time
        self.cpu_bursts = cpu_bursts
        self.intervals = deepcopy(intervals)
        self.io_process = io_process
        
    def print(self, process_name):
        if (self.io_process):
            print("{}-bound process {}: arrival time {}ms; {} CPU bursts:".format("I/O", process_name, self.arrival_time, self.cpu_bursts))
        else:
            print("{}-bound process {}: arrival time {}ms; {} CPU bursts:".format("CPU", process_name, self.arrival_time, self.cpu_bursts))
        
        for i in range(0, len(self.intervals) - 1):
            if not i%2 == 0:
                print("--> I/O burst {}ms".format(self.intervals[i]))
            else:
                print("--> CPU burst {}ms".format(self.intervals[i]), end = " ")
                
        print("--> CPU burst {}ms".format(self.intervals[-1]))
        
        
        
class Generator(object):
    def __init__(self, lamda, upper_bound, seed):
        self.lamda = lamda
        self.start = rand.rand48(seed)
        self.upper_bound = upper_bound

    def next_exp(self):
        # uniform random variable to exponential
        next_val = self.upper_bound+1
        while(next_val > self.upper_bound):
            next_val = -math.log(self.start.drand48())
            next_val = next_val / self.lamda
        return next_val
    
    def next_process(self, io_process_bool):
        gaps = []
        first_arrival_time = math.floor(self.next_exp())
        cpu_num_bursts = math.ceil(100 * self.start.drand48())
        for _ in range(cpu_num_bursts - 1):
            cpu_burst_time = math.ceil(self.next_exp())
            io_burst_time = math.ceil(self.next_exp()) * 10
            if not io_process_bool:
                cpu_burst_time *= 4
                io_burst_time//=4
            gaps.append(cpu_burst_time)
            gaps.append(io_burst_time)

        cpu_burst_time = math.ceil(self.next_exp())
        if not io_process_bool:
           cpu_burst_time *= 4
        gaps.append(cpu_burst_time)

        return Process(first_arrival_time, cpu_num_bursts, gaps, io_process_bool)
        
        


        
    
