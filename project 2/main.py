import sys
from copy import deepcopy
import math
from string import ascii_uppercase as process_id_set

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
    def __init__(self, lamda, ubound, seed):
        self.lamda = lamda
        self.engine = rand48(seed)
        self.ubound = ubound

    def next_exp(self):


        # uniform random variable to exponential
        out = self.ubound+1
        while(out > self.ubound):
            out = -math.log(self.engine.drand48()) / self.lamda
        return out
    
    def next_process(self, io_bound:bool):
    
        initial_arrival_time = math.floor(self.next_exp())
        cpu_bursts = math.ceil(100 * self.engine.drand48())
        intervals = []
        for _ in range(cpu_bursts - 1):
            cpu_burst_time = math.ceil(self.next_exp())
            io_time = math.ceil(self.next_exp()) * 10
            if not io_bound:
                cpu_burst_time*=4
                io_time//=4
            intervals.append(cpu_burst_time)
            intervals.append(io_time)

        cpu_burst_time = math.ceil(self.next_exp())
        if not io_bound:
           cpu_burst_time*=4
        intervals.append(cpu_burst_time)

        return Process(initial_arrival_time, cpu_bursts, intervals, io_bound)



def print_start(process_count, cpu_count):
    if (cpu_count == 1):
        print("<<< PROJECT PART I -- process set (n={}) with {} CPU-bound {} >>>".format(process_count, cpu_count, "process"))
    else:
        print("<<< PROJECT PART I -- process set (n={}) with {} CPU-bound {} >>>".format(process_count, cpu_count, "processes"))

if __name__ == '__main__':
        # exec arg validation
        if not len(sys.argv) == 6:
            print("ERROR: USAGE:python3 project.py <n_proc: int> <n_cpu: int> <seed: int> <lambda: float> <ubound: int>")
            exit(1)

        # Runtime vars
        n_processes = 0
        n_cpu = 0
        rand48_seed = 0
        exp_lambda = 0.0
        exp_ubound = 0
        try:
            n_processes = int(sys.argv[1])
        except:
            print("ERROR: n_processes should be an integer.")
            exit(1)
        try:
            n_cpu = int(sys.argv[2])
        except:
            print("ERROR: n_cpu should be an integer.")
            exit(1)
        try:
            rand48_seed = int(sys.argv[3])
        except:
            print("ERROR: rand48_seed should be an integer.")
            exit(1)
        try:
            exp_lambda = float(sys.argv[4])
        except:
            print("ERROR: exp_lambda should be a float/double.")
            exit(1)
        try:
            exp_ubound = int(sys.argv[5])
        except:
            print("ERROR: exp_ubound should be an integer.")
            exit(1)

        if n_cpu > n_processes:
            print("ERROR: n_proc >= n_cpu")
            exit(1)

        # rand
        gen = Generator(exp_lambda, exp_ubound, rand48_seed)
        print("<<< PROJECT PART I -- process set (n={}) with {} CPU-bound {} >>>".format(n_processes, n_cpu, "process" if n_cpu == 1 else "processes" ))
        
        processes = [] 
        for i in range(n_processes):
            io_bound = i < n_processes - n_cpu
            if io_bound:
                p = gen.next_process(True)
            else:
                p = gen.next_process(False)
            if p:
                processes.append(p)
            else:
                i-=1
        
        for i in range(len(processes)):
            processes[i].print(process_id_set[i])
