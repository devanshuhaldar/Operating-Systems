import sys
import math
from copy import deepcopy
from string import ascii_uppercase as process_id_set

class rand48:
    def __init__(self, seed):
        self.a = 0x5DEECE66D
        self.b = 0xB
        self.x = int(bin(seed)[2:].zfill(32) + bin(0x330E)[2:].zfill(16), 2)
        self.y = 2**48

    def get_next(self):
        self.x = (self.a * self.x + self.b) & (self.y - 1)
        return self.x
    
    def drand48(self):
        return self.get_next() / self.y

    
class Process():
    def __init__(self, arrival_time, gaps, cpu_bursts, io_bool):
        self.arrival_time = arrival_time
        self.cpu_bursts = cpu_bursts
        self.gaps = deepcopy(gaps)
        self.io_bool = io_bool
        
    def print(self, process_name):
        if(self.io_bool == True):
            print("{}-bound process {}: arrival time {}ms; {} CPU bursts:".format("I/O", process_name, self.arrival_time, self.cpu_bursts))
        else:
            print("{}-bound process {}: arrival time {}ms; {} CPU bursts:".format("CPU", process_name, self.arrival_time, self.cpu_bursts))
        
        for i in range(0, len(self.gaps) - 1):
            if not i%2 == 0:
                print("--> I/O burst {}ms".format(self.gaps[i]))  
            else:
                print("--> CPU burst {}ms".format(self.gaps[i]), end = " ")
                
        print("--> CPU burst {}ms".format(self.gaps[-1]))
        

class Generator():
    def __init__(self, seed, lambda_val, upper_bound):
        self.first_rand = rand48(seed)
        self.lambda_val = lambda_val
        self.upper_bound = upper_bound

    def get_next_ub(self):
        next_ub = self.upper_bound+1
        while(self.upper_bound < next_ub):
            # -log( r ) / lambda
            next_ub = -math.log(self.first_rand.drand48()) / self.lambda_val
        return next_ub
    
    def next_process(self, io_bool):
        gaps = []
        arrival_time = math.floor(self.get_next_ub())
        cpu_bursts = math.ceil(100 * self.first_rand.drand48())
        for _ in range(cpu_bursts - 1):
            cpu_burst_time = math.ceil(self.get_next_ub())
            io_burst_time = math.ceil(self.get_next_ub()) * 10
            if(io_bool == False):
                io_burst_time//=4
                cpu_burst_time*=4
            gaps.append(cpu_burst_time)
            gaps.append(io_burst_time)

        cpu_burst_time = math.ceil(self.get_next_ub())
        if not io_bool:
           cpu_burst_time*=4
        gaps.append(cpu_burst_time)

        return Process(arrival_time, gaps, cpu_bursts, io_bool)
        
        



if __name__ == '__main__':
    if not len(sys.argv) == 6:
        print("ERROR: USAGE:python3 project.py <n_proc: int> <num_cpu: int> <seed: int> <lambda: float> <upper_bound: int>")
        exit(1)

    num_processes = 0
    num_cpu = 0
    rand48_seed = 0
    exponential_lam_val = 0.0
    exponential_ub = 0
    try:
        num_processes = int(sys.argv[1])
    except:
        print("ERROR: num_processes has to be an integer.")
        exit(1)
    try:
        num_cpu = int(sys.argv[2])
    except:
        print("ERROR: num_cpu has to be an integer.")
        exit(1)
    try:
        rand48_seed = int(sys.argv[3])
    except:
        print("ERROR: rand48_seed has to be an integer.")
        exit(1)
    try:
        exponential_lam_val = float(sys.argv[4])
    except:
        print("ERROR: exponential_lam_val has to be a float/double.")
        exit(1)
    try:
        exponential_ub = int(sys.argv[5])
    except:
        print("ERROR: exponential_ub has to be an integer.")
        exit(1)

    if num_cpu > num_processes:
        print("ERROR: num_process >= num_cpu")
        exit(1)


    if (num_cpu == 1):
        print("<<< PROJECT PART I -- process set (n={}) with {} CPU-bound {} >>>".format(num_processes, num_cpu, "process"))
    else:
        print("<<< PROJECT PART I -- process set (n={}) with {} CPU-bound {} >>>".format(num_processes, num_cpu, "processes"))
    
    rand_gen = Generator(rand48_seed, exponential_lam_val, exponential_ub)
    processes = [] 
    for i in range(num_processes):
        io_bool = i < num_processes - num_cpu
        if (io_bool == False):
            process = rand_gen.next_process(False)
        else:
            process = rand_gen.next_process(True)
            
        if process:
            processes.append(process)
        else:
            i-=1
    
    for i in range(len(processes)):
        processes[i].print(process_id_set[i]) 