#Op Sys Project Part 1 and 2 Combined
# Devanshu & Michael

import sys
import math
import copy
from math import ceil
import operator

#Random 
class RandomGenerator48(object):
    def __init__(self, seed):
        self.n = seed

    def seed(self, seed):
        self.n = seed

    def srand(self, seed):
        self.n = ((seed << 16) | 0x330E)

    def generate_next(self):
      self.n = (0x5DEECE66D * self.n + 0xB) & ((1 << 48) - 1)
      return self.n

    def drand(self):
        return self.generate_next() / 2 ** 48

    def lrand(self):
        return self.generate_next() >> 17

    def mrand(self):
        n = self.generate_next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n

class Process(object):
  def __init__(self, parameters):
    self.cpu_burst_array, self.io_burst_array, self.io_bound_array, self.cpu_array = [], [], [], []

    ascii_start = 65
    ascii_end = ascii_start + 6
    if (parameters[0]<=25):
      self.id = ascii_start + parameters[0]
    else:
      self.id = ascii_end + parameters[0] 

    self.arrival_time = parameters[1]
    self.cpu_burst_count = parameters[2]
    self.cpu_t_predict = parameters[3]
    self.lamb = parameters[4]
    self.rand48 = parameters[5]
    self.upper_bound = parameters[6]
    self.cpu_bound = parameters[7]
    self.n_process, self.run_burst, self.wait_time = 0,0,0

    
    for i in range(self.cpu_burst_count):
      if(self.cpu_bound!=1):
        output = "I/O-bound process"
        temp=self.next_exp()
        self.cpu_burst_array.append(temp)
        self.io_bound_array.append(temp)
        val = self.cpu_burst_count - 1
        if(i == val):
          break
        temp=self.next_exp()
        self.io_burst_array.append(temp*10)
      else:
        output = "CPU-bound process"
        temp = self.next_exp()*4
        self.cpu_burst_array.append(temp)
        self.cpu_array.append(temp)
        val = self.cpu_burst_count - 1
        if(i == val):
          break
        self.io_burst_array.append(math.floor(self.next_exp()*10/8))

    out = ""
    if(self.cpu_burst_count>1):
      out = "bursts"
    else: out = "burst"

    print("{} {}: arrival time {}ms; {} CPU {}".format(output,chr(self.id),self.arrival_time,self.cpu_burst_count,out))
    self.remain = self.cpu_t_predict - self.run_burst
  
  def new_ready(self):
    self.remain = self.cpu_t_predict - self.run_burst

  def check_end(self):
    if (self.n_processes >= self.cpu_burst_count):
      return True
    return False

  def get_id(self):
    return self.id

  def get_arr(self):
    return self.arrival_time

  def add_num_proc(self):
    self.n_process = self.n_process + 1

  def get_num_proc(self):
    return self.n_process

  def get_cpu_pre_time(self):
    index = self.n_process - 1
    return self.cpu_burst_array[index]

  def get_cpu_time(self):
    index = self.n_process
    return self.cpu_burst_array[index]

  def get_io_time(self):
    index = self.n_process
    length = len(self.io_burst_array) - 1
    if(index <= length):
      return self.io_burst_array[index]
    else:
      return 0

  def next_exp(self):
    while 1 == 1:
      temp = math.log(self.rand48.drand())
      arrival_time =  math.ceil((temp/self.lamb)*-1.0)
      if(arrival_time <= self.upper_bound):
        return arrival_time

def result_out(number):
  value = 1000
  return math.ceil(number * value) / value

def rand(rand48,in_lambda,up_bound):
  while 1 == 1:
    temp = math.log(rand48.drand())
    ret =(temp /in_lambda)*-1
    if(ret <= up_bound):
      return ret

class FCFS(object):
  def __init__(self,ctsw,data,t_cs):
    self.time = 0
    self.inoutprocess = []
    self.time_context_switch =ctsw
    self.processList = copy.deepcopy(data)
    self.running, self.io_run = False, False
    self.current_io_run_to,self.process_terminate, self.cpu_switch= 0, 0, 0
    self.time_slice = t_cs
    self.total_wait, self.cpu_wait_time, self.total_switch, self.total_preempt  = 0, 0, 0, 0
  
  def wait_queue_append(self,queue):
    for i in queue:
      i.wait_time += 1

  def queue_to_string(self,queue):
    result = ""
    for process in queue:
      result += chr(process.get_id())
    return result

  def arrival_flag(self,queue):
    temp = 0
    for i in self.processList:
      if(i.get_arr() == self.time):
        temp = 1
        queue.append(i)
        if(self.time < 10000):
          print("time {}ms: Process {} arrived; added to ready queue [Q {}]".format(self.time,chr(i.get_id()),' '.join(self.queue_to_string(queue))))
    if(temp != 1):
      return False
    else:
      return True

  def context_switch_zero(self,queue,proc):
    self.total_switch += 1
    if proc.cpu_bound == 1:
        self.cpu_switch += 1

    half_time_context_switch = self.time_context_switch // 2
    for i in range(half_time_context_switch):
        self.time += 1
        self.wait_queue_append(queue)
        if i < half_time_context_switch - 1:
            self.arrival_flag(queue)
            self.io_terminated_q(queue)

  def base_case(self,queue):
    self.arrival_flag(queue)
    self.io_terminated_q(queue) 

  def context_switch(self,queue,proc):
    self.total_switch +=1
    if(proc.cpu_bound == 1):
      self.cpu_switch+=1
    i = 0 
    half_context_switch = (self.time_context_switch) // 2
    while i < half_context_switch:
        self.time = self.time + 1
        self.wait_queue_append(queue)
        self.arrival_flag(queue)
        self.io_terminated_q(queue)
        i  = i + 1

  def time_plus(self,time,queue):
    i = 0 
    while i < range(time):
      self.time = self.time + 1
      self.arrival_flag(queue)
      i = i + 1

  def cpu_burst(self,input_of_time,queue,proc):
    flag = self.time < 10000

    if flag: 
      if(len(queue) != 0):
        print("time {}ms: Process {} started using the CPU for {}ms burst [Q {}]".format(self.time,chr(proc.get_id()),input_of_time,' '.join(self.queue_to_string(queue))))
      else:
        print("time {}ms: Process {} started using the CPU for {}ms burst [Q <empty>]".format(self.time,chr(proc.get_id()),input_of_time))
        
    self.base_case(queue)
    self.running = True
    
    for i in range(input_of_time - 1):
      self.time += 1
      self.wait_queue_append(queue)
      if(i < input_of_time - 1):
        self.arrival_flag(queue)
      if not (self.io_run):
        pass
      else:
        self.io_terminated_q(queue)
      
    proc.add_num_proc()
    self.running = False
    
    self.time +=1
    self.wait_queue_append(queue)
    
    new_flag = self.time < 10000
    if(proc.n_process < proc.cpu_burst_count):
      if(len(queue) == 0):
        if(proc.cpu_burst_count - proc.n_process != 1):
          if(new_flag):
            print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q <empty>]".format(self.time,chr(proc.get_id()),proc.cpu_burst_count - proc.n_process))
          else:
            if(new_flag):
             print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q <empty>]".format(self.time,chr(proc.get_id()),proc.cpu_burst_count - proc.n_process))
      else:
        if(proc.cpu_burst_count - proc.n_process != 1):
          if(new_flag):
            print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q {}]".format(self.time,chr(proc.get_id()),proc.cpu_burst_count - proc.n_process,' '.join(self.queue_to_string(queue))))
        else: 
          if(new_flag):
            print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q {}]".format(self.time,chr(proc.get_id()),proc.cpu_burst_count - proc.n_process,' '.join(self.queue_to_string(queue))))
          
    else:
      if(proc.cpu_bound!=1): pass
      else:
        self.cpu_wait_time += proc.wait_time
      self.total_wait += proc.wait_time
      if(len(queue) != 0 ):
        print("time {}ms: Process {} terminated [Q {}]".format(self.time,chr(proc.get_id()),' '.join(self.queue_to_string(queue))))
        self.arrival_flag(queue)
        self.io_terminated_q(queue)
        self.context_switch(queue,proc)
        
      else:
        print("time {}ms: Process {} terminated [Q <empty>]".format(self.time,chr(proc.get_id())))
        self.arrival_flag(queue)
        self.io_terminated_q(queue)
        self.context_switch(queue,proc)
        
  def io_buffer(self,input_of_time,queue,proc):
    self.io_run = True
    temp_time = copy.deepcopy(self.time)

    flag = self.time < 10000
    if(len(queue) != 0):
      if(flag):
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q {}]".format(temp_time,chr(proc.get_id()),self.time+input_of_time+self.time_context_switch//2,' '.join(self.queue_to_string(queue))))
    else:
      if(flag):
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q <empty>]".format(temp_time,chr(proc.get_id()),self.time+input_of_time+self.time_context_switch//2))
      
    self.arrival_flag(queue)
    self.io_terminated_q(queue)
    self.context_switch(queue,proc)
    self.io_run = True
    io_run_to = int(self.time + input_of_time)
    self.inoutprocess.append([proc,io_run_to])
    self.inoutprocess.sort(key = lambda x:x[1])

  def io_terminated_q(self,queue):
    checks1 = 0
    self.inoutprocess.sort(key = lambda x:[x[1],x[0].get_id()])
    while_it = 0
    if(len(self.inoutprocess)!= 0):
      while(while_it < len(self.inoutprocess)):
        if(self.time != self.inoutprocess[while_it][1]):
          while_it +=1
        else:
          checks1 = 1
          queue.append(self.inoutprocess[while_it][0])
          if(self.time < 10000):
            print("time {}ms: Process {} completed I/O; added to ready queue [Q {}]"\
              .format(self.time,chr(self.inoutprocess[while_it][0].get_id()),' '.join(self.queue_to_string(queue))))
          self.inoutprocess.pop(while_it)
          while_it = 0
          if(len(self.inoutprocess) == 0):
            self.io_run = False
    
    if(checks1 != 1):
      return False
    else:
      return True

  def time_slice_flag(self,queue,input_of_time): 
    if(input_of_time <= self.time_slice):
      return False
    return True

  def algorithm_terminated_flag(self,queue):
    for i in queue:
      if(i.check_end() == False):
        return i.check_end()
    return True

  def temp_output(self):
    count_total_burst_time = sum(sum(process.cpu_burst_array) for process in self.processList)
    count_total_io_time = sum(sum(process.io_bound_array) for process in self.processList)
    count_total_cpu = sum(sum(process.cpu_array) for process in self.processList)

    count_burst = sum(len(process.cpu_burst_array) for process in self.processList)
    count_io = sum(len(process.io_bound_array) for process in self.processList)
    count_cpu = sum(len(process.cpu_array) for process in self.processList)

    temp = self.total_wait + count_total_burst_time + self.time_context_switch * (self.total_switch // 2)
    temp1 = self.cpu_wait_time + count_total_cpu + self.time_context_switch * (self.cpu_switch // 2)
    temp2 = (self.total_wait - self.cpu_wait_time) + count_total_io_time + self.time_context_switch * ((self.total_switch - self.cpu_switch) // 2)

    a = count_total_burst_time / self.time
    b = count_total_burst_time / count_burst if count_burst else 0
    e = self.total_wait / count_burst if count_burst else 0
    c = count_total_cpu / count_cpu if count_cpu else 0
    f = self.cpu_wait_time / count_cpu if count_cpu else 0
    k = temp1 / count_cpu if count_cpu else 0
    h = temp / count_burst if count_burst else 0
    d = count_total_io_time / count_io if count_io else 0
    g = (self.total_wait - self.cpu_wait_time) / count_io if count_io else 0
    L = temp2 / count_io if count_io else 0
    m, n, o = self.total_switch // 2, self.cpu_switch // 2, (self.total_switch - self.cpu_switch) // 2
    r, s, t = self.total_preempt, 0, self.total_preempt - 0

    return ["FCFS", a, b, c, d, e, f, g, h, k, L, m, n, o, r, s, t]
#fcfc main
  def FCFS(self):
    print("time {}ms: Simulator started for {} [Q <empty>]".format(self.time,"FCFS"))
    queue = []
    while 1 == 1:
      if(self.running == False and len(queue) != 0):
        proc = copy.deepcopy(queue[0])
        queue.pop(0)
        self.context_switch_zero(queue,proc)
        cpu_burst_time_temp, io_burst_time_temp= proc.get_cpu_time(), proc.get_io_time()
        self.cpu_burst(cpu_burst_time_temp,queue,proc)
        if(io_burst_time_temp == 0):
          self.process_terminate += 1
          continue
        else:
          self.io_buffer(io_burst_time_temp,queue,proc)
          continue

      if len(queue) == 0:
        if (self.running == False):
          if self.io_run == False:
            if self.process_terminate != 0:
              break
      
      if(self.running == False):
        ck1 = self.arrival_flag(queue)
        if(ck1 != True):
          pass
        else:
          continue
        if(self.io_run):
          ck2 = self.io_terminated_q(queue)
          if(ck2 == False):
            pass
          else:
            continue

        self.time +=1
        self.wait_queue_append(queue)
        self.arrival_flag(queue)

        if(self.io_run):
          self.io_terminated_q(queue)

    print("time {}ms: Simulator ended for FCFS [Q <empty>]".format(self.time))

class SRT1(object):
  def __init__(self,ctsw,data,t_cs,alpha_constant):
    self.time = 0

    self.time_context_switch = ctsw
    self.alpha = alpha_constant

    self.processList = copy.deepcopy(data)
    self.running, self.io_run = False, False
    self.current_io_run_to, self.process_terminate = 0, 0
    self.process_in_CPU,self.in_io_process, self.complete = [],[],[]
    self.cpu_swit, self.total_wait, self.cpu_wait_time, self.context_switch_sum, self.total_preempt, self.preemption_in_cpu = 0,0,0,0,0,0

  def wait_time_add(self,queue):
    for process in queue:
      process.wait_time += 1
    for i in self.complete:
      i.wait_time +=1

  def to_str(self,queue):
    ret = ""
    for i in queue:
      ret += chr(i.get_id())
    return ret

  def get_proc_cpu_time(self,proc):
    temp = proc.get_cpu_time()
    if(proc.run_burst != 0):
      res = temp - proc.run_burst
      return res
    else:
      return temp

  def arrival_flag(self,queue):
    flag = False
    temp = 0
    for i in self.processList:
      if(i.get_arr() == self.time):
        temp = 1
        queue.append(i)
        queue.sort(key = operator.attrgetter("remain","id"))
        temp_flag = self.time < 10000
        if temp_flag:
          print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue [Q {}]".format(self.time,chr(i.get_id()),i.cpu_t_predict,' '.join(self.to_str(queue))))
      
    if(temp != 1):
      return flag
    else:
      return not flag

  def base_case(self,queue,proc):
    self.context_switch_sum +=1
    if(proc.cpu_bound == 1):
      self.cpu_swit+=1
    div2 = (self.time_context_switch)//2
    for i in range(div2):
      self.time +=1
      self.wait_time_add(queue)
      self.arrival_flag(queue)
      if(i < div2 - 1):
        self.io_terminated_q(queue) 

  def context_switch_add(self,queue,proc):
    self.context_switch_sum = self.context_switch_sum + 1
    if(proc.cpu_bound == 1):
      self.cpu_swit+=1
    div2 = (self.time_context_switch)//2
    for i in range(div2):
      self.time +=1
      if(i==div2-1):
        if(len(self.complete)!=0):
          self.complete[0].new_ready()
          queue.append(self.complete[0])
          self.complete.pop(0)
          queue.sort(key = operator.attrgetter("remain","id"))
      self.wait_time_add(queue)
      self.arrival_flag(queue)
      self.io_terminated_q(queue)
    
    if(len(self.complete)!=0):
        self.complete[0].new_ready()
        queue.append(self.complete[0])
        self.complete.pop(0)
        queue.sort(key = operator.attrgetter("remain","id"))

  def time_plus(self,time,queue):
    for _ in range(time):
      self.time = self.time + 1
      self.arrival_flag(queue)

  def cpu_burst(self,time_in,queue,proc):
    output= []
    if(len(queue)!=0):
      output = ' '.join(self.to_str(queue))
    else:
      output = "<empty>"

    temp_flag = self.time < 10000
    if temp_flag:
      if(proc.run_burst != 0): 
        print("time {}ms: Process {} (tau {}ms) started using the CPU for remaining {}ms of {}ms burst [Q {}]"\
        .format(self.time,chr(proc.get_id()),proc.cpu_t_predict,proc.get_cpu_time() - proc.run_burst,proc.get_cpu_time(),output))
        
      else:
        print("time {}ms: Process {} (tau {}ms) started using the CPU for {}ms burst [Q {}]"\
        .format(self.time,chr(proc.get_id()),proc.cpu_t_predict,time_in,output))
        
    self.process_in_CPU= []
    self.process_in_CPU.append(proc)
    self.running = True
    check_c =self.io_terminated_q(queue)
    if(check_c == 2):
      self.running = False
      return False
    
    if(len(queue) != 0 and queue[0].remain < proc.remain):
      if(self.time < 10000):
        print("time {}ms: Process {} (tau {}ms) will preempt {} [Q {}]".format(self.time,chr(queue[0].get_id()),\
        queue[0].cpu_t_predict,chr(proc.get_id()),' '.join(self.to_str(queue)) ))
      self.total_preempt +=1
      if(proc.cpu_bound == 1):
        self.preemption_in_cpu += 1
      self.total_wait -= self.time_context_switch//2
      if(proc.cpu_bound==1):
        self.cpu_wait_time -= self.time_context_switch//2
      queue.append(proc)
      proc.new_ready()
      self.running = False
      queue.sort(key = operator.attrgetter("remain","id"))
      return False

    for i in range(time_in):
      self.time += 1
      self.wait_time_add(queue)
      proc.run_burst+= 1
      if(i < time_in - 1):
        self.arrival_flag(queue)
      if i < time_in - 1:
        if self.io_run:
          check_c = self.io_terminated_q(queue)
          if(check_c == 2):
            self.running = False
            return self.running
    
    res = proc.get_cpu_time() - proc.run_burst
    if(res != 0):
      queue.append(proc)
      proc.new_ready()
      queue.sort(key = operator.attrgetter("remain","id"))
      self.arrival_flag(queue)
      self.io_terminated_q(queue)
      self.running = False
      return self.running
    else:
      proc.run_burst = 0
      proc.n_process+=1
      
    self.running = False
    
    if(len(queue) != 0):
      output = "<empty>"
    else:
      output = ' '.join(self.to_str(queue))
      
    if(proc.get_num_proc() < proc.cpu_burst_count):
      tmp = copy.deepcopy(proc.cpu_t_predict)
      key = chr(proc.id)
      tau = proc.cpu_t_predict
      alpha = self.alpha
      cpu_pre_time = proc.get_cpu_pre_time()
      tau = (tau * float(1 - float(alpha))) + (float(cpu_pre_time) * float(alpha))
      proc.cpu_t_predict = ceil(tau)
      proc.remain = proc.cpu_t_predict
      
      if(proc.cpu_burst_count - proc.n_process > 0):
        proc.run_burst = 0
        if self.time < 10000:
            bursts_left = proc.cpu_burst_count - proc.n_process
            burst_word = "burst" if bursts_left == 1 else "bursts"
            print(f"time {self.time}ms: Process {chr(proc.get_id())} (tau {tmp}ms) completed a CPU burst; {bursts_left} {burst_word} to go [Q {output}]")
            print(f"time {self.time}ms: Recalculating tau for process {chr(proc.get_id())}: old tau {tmp}ms ==> new tau {proc.cpu_t_predict}ms [Q {output}]")
      else:
        if self.time < 10000:
          bursts_left = proc.cpu_burst_count - proc.n_process
          queue_status = "[Q <empty>]" if not queue else f"[Q {' '.join(self.to_str(queue))}]"
          burst_word = "burst" if bursts_left == 1 else "bursts"
          
          print(f"time {self.time}ms: Process {chr(proc.get_id())} (tau {tmp}ms) completed a CPU burst; {bursts_left} {burst_word} to go {queue_status}")
          print(f"time {self.time}ms: Recalculating tau for process {chr(proc.get_id())}: old tau {tmp}ms ==> new tau {proc.cpu_t_predict}ms {queue_status}")
    else:
      self.total_wait += proc.wait_time
      if(proc.cpu_bound==1):
        self.cpu_wait_time += proc.wait_time
      if(len(queue) != 0 ):
        print("time {}ms: Process {} terminated [Q {}]".format(self.time,chr(proc.get_id()),' '.join(self.to_str(queue))))
        
      else:
        print("time {}ms: Process {} terminated [Q <empty>]".format(self.time,chr(proc.get_id())))
      self.context_switch_add(queue,proc)
        
  def io_buffer(self,time_in,queue,proc):
    self.io_run = True
    temp_time = copy.deepcopy(self.time)
    temp_flag = self.time < 10000
    if temp_flag: 
      if(len(queue) == 0):
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q <empty>]"\
            .format(temp_time,chr(proc.get_id()),self.time+time_in+self.time_context_switch//2))
      else:
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q {}]"\
            .format(temp_time,chr(proc.get_id()),self.time+time_in+self.time_context_switch//2,' '.join(self.to_str(queue))))

    self.arrival_flag(queue)
    self.io_terminated_q(queue)
    self.context_switch_add(queue,proc)
    io_run_to = int(self.time + time_in)
    self.io_run = True
    self.in_io_process.append([proc,io_run_to])
    self.in_io_process.sort(key = lambda x:x[1])

  def io_terminated_q(self,queue):
    checks1 = 0
    flag = False
    self.in_io_process.sort(key = lambda x:[x[1],x[0].get_id()])
    while_it = 0
    one =  1
    if(len(self.in_io_process)!= 0):
      while(while_it < len(self.in_io_process)):
        if(self.time == self.in_io_process[while_it][one]):
          if(len(self.process_in_CPU) == one):
            for i in queue:
                i.new_ready()
            if((self.process_in_CPU[0].cpu_t_predict - self.process_in_CPU[0].run_burst > self.in_io_process[while_it][0].cpu_t_predict)):
              if flag == False:
                if self.running == True:
                  queue.append(self.in_io_process[while_it][0])
                  checks1 = 2
                  for i in queue:
                    i.new_ready()
                  queue.sort(key = operator.attrgetter("remain","id"))
                  if self.time < 10000:
                    print("time {}ms: Process {} (tau {}ms) completed I/O preempting {} [Q {}]".format(\
                  self.time,chr(self.in_io_process[while_it][0].get_id()),self.in_io_process[while_it][0].cpu_t_predict,\
                  chr(self.process_in_CPU[0].get_id()), ' '.join(self.to_str(queue))))
                  if(self.process_in_CPU[0].cpu_bound == 1):
                    self.preemption_in_cpu = self.preemption_in_cpu + 1

                  if(self.process_in_CPU[0].cpu_bound==1):
                    self.cpu_wait_time -= self.time_context_switch//2

                  self.complete.append(self.process_in_CPU[0])
                  self.in_io_process.pop(while_it)
                  while_it = 0
                  flag = True
                  self.total_preempt +=1
                  self.total_wait -= self.time_context_switch//2
                  continue
            else:
              if(checks1 != 2):
                checks1 = 1
          queue.append(self.in_io_process[while_it][0])
          for i in queue:
            i.new_ready()
          queue.sort(key = operator.attrgetter("remain","id"))
          if(self.time < 10000):
            print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue [Q {}]"\
            .format(self.time,chr(self.in_io_process[while_it][0].get_id()),self.in_io_process[while_it][0].cpu_t_predict,' '.join(self.to_str(queue))))
          self.in_io_process.pop(while_it)
          while_it = 0
          if(len(self.in_io_process) == 0):
            self.io_run = False
        else:
          while_it +=1

    if(checks1 == 1):
      return 1
    if(checks1 == 2):
      return 2
    return 0

  def check_time_slice(self,queue,time_in):
    if(time_in <= self.time_slice):
      return False
    return True

  def check_alg_finish(self,queue):
    for process in queue:
      if(process.check_end() == False):
        return False
    return True

  def temp_output(self):
    count_total_burst_time = sum(sum(p.cpu_burst_array) for p in self.processList)
    count_total_io_time = sum(sum(p.io_bound_array) for p in self.processList)
    count_total_cpu = sum(sum(p.cpu_array) for p in self.processList)

    count_burst = sum(len(p.cpu_burst_array) for p in self.processList)
    count_io = sum(len(p.io_bound_array) for p in self.processList)
    count_cpu = sum(len(p.cpu_array) for p in self.processList)

    temp = self.total_wait + count_total_burst_time + self.time_context_switch * (self.context_switch_sum // 2)
    temp1 = self.cpu_wait_time + count_total_cpu + self.time_context_switch * (self.cpu_swit // 2)
    temp2 = (self.total_wait - self.cpu_wait_time) + count_total_io_time + self.time_context_switch * ((self.context_switch_sum - self.cpu_swit) // 2)

    mutex = lambda x, y: x / y if y else 0

    a = mutex(count_total_burst_time, self.time)
    b = mutex(count_total_burst_time, count_burst)
    c = mutex(count_total_cpu, count_cpu)
    d = mutex(count_total_io_time, count_io)
    e = mutex(self.total_wait, count_burst)
    f = mutex(self.cpu_wait_time, count_cpu)
    g = mutex(self.total_wait - self.cpu_wait_time, count_io)
    h = mutex(temp, count_burst)
    k = mutex(temp1, count_cpu)
    L = mutex(temp2, count_io)
    m, n, o = self.context_switch_sum // 2, self.cpu_swit // 2, (self.context_switch_sum - self.cpu_swit) // 2
    r = self.total_preempt
    s = self.preemption_in_cpu
    t = self.total_preempt - self.preemption_in_cpu

    return ["SRT", a, b, c, d, e, f, g, h, k, L, m, n, o, r, s, t]

  def SRT(self):
    print("time {}ms: Simulator started for {} [Q <empty>]".format(self.time,"SRT"))
    queue = []
    while 1 == 1:
      if(self.running == False and len(queue) != 0):
        proc = copy.deepcopy(queue[0])
        
        queue.pop(0)
        self.base_case(queue,proc)
        cpu_burst_time_temp = self.get_proc_cpu_time(proc) 
        io_burst_time_temp = proc.get_io_time()
        
        check = self.cpu_burst(cpu_burst_time_temp,queue,proc)
        if(check == False):
          self.context_switch_add(queue,proc)
          continue

        if(io_burst_time_temp == 0):
          self.process_terminate += 1
          continue
        else:
          self.io_buffer(io_burst_time_temp,queue,proc)
          continue
          
      if(len(queue) == 0 and self.running == False and self.io_run == False\
       and self.process_terminate != 0):
        break

      if(self.running == False):
        ck1 = self.arrival_flag(queue)
        if(ck1 == True):
          continue
        if(self.io_run):
          ck2 = self.io_terminated_q(queue)
          if(ck2 == 1):
            continue
        self.time += 1
        self.wait_time_add(queue)

        self.arrival_flag(queue)

        if(self.io_run):

          self.io_terminated_q(queue)

    print("time {}ms: Simulator ended for SRT [Q <empty>]".format(self.time))

class SJF(object):
  def __init__(self,ctsw,data,t_cs,alpha):
    self.time = 0
    self.taus = {}
    self.time_context_switch = ctsw
    self.alpha = alpha
    
    self.processList = copy.deepcopy(data)
    for i in self.processList:
      self.taus[chr(i.id)] = i.cpu_t_predict
    self.running, self.io_run = False, False
    self.current_io_run_to, self.process_terminate = 0, 0
    self.inoutprocess, self.io_complete = [], []
    self.total_wait,  self.cpu_wait_time, self.total_switch, self.cpu_switch, self.total_preempt = 0, 0, 0, 0, 0
   
  def increment_wait_times(self,queue):
    for process in queue:
      process.wait_time += 1

  def queue_to_string(self,queue):
    ret = ""
    for i in queue:
      ret += chr(i.get_id())
    return ret

  def arrival_checker(self,queue):
    arrived = False 
    for process in self.processList:
        if process.get_arr() == self.time:
            arrived = True
            insertion_point = next((index for index, q_process in enumerate(queue) if process.get_id() < q_process.get_id() and q_process.get_id() not in self.io_complete), len(queue))
            queue.insert(insertion_point, process)
            flag = self.time < 10000
            if flag:
                print(f"time {self.time}ms: Process {chr(process.get_id())} (tau {self.taus[chr(process.get_id())]}ms) arrived; added to ready queue [Q {' '.join(self.queue_to_string(queue))}]")

    return arrived

  def context_switch_zero(self,queue,proc):
    self.total_switch = self.total_switch + 1
    if(proc.cpu_bound == 1):
      self.cpu_switch+=1
    r = (self.time_context_switch)//2
    for i in range(r):
      self.time +=1
      self.increment_wait_times(queue)
      if(i < r - 1):
        self.arrival_checker(queue)
        self.io_terminated_q(queue) 

  def time_zero(self,queue):
    self.arrival_checker(queue)
    self.io_terminated_q(queue) 

  def context_switch_add(self,queue,proc):
    self.total_switch +=1
    if(proc.cpu_bound == 1):
      self.cpu_switch+=1

    r = (self.time_context_switch)//2
    for i in range(r):
      self.time = self.time + 1
      self.increment_wait_times(queue)
      self.arrival_checker(queue)
      self.io_terminated_q(queue)

  def time_plus(self,time,queue):
    for i in range(time):
      self.time = self.time + 1
      self.arrival_checker(queue)

  def cpu_burst(self,input_of_time,queue,proc):
    flag = self.time < 10000  

    queue_status = "[Q <empty>]" if not queue else f"[Q {' '.join(self.queue_to_string(queue))}]"
    if flag:
        print(f"time {self.time}ms: Process {chr(proc.get_id())} (tau {self.taus[chr(proc.id)]}ms) started using the CPU for {input_of_time}ms burst {queue_status}")

    self.time_zero(queue)
    self.running = True
    for _ in range(input_of_time - 1):
        self.time += 1
        self.increment_wait_times(queue)
        self.arrival_checker(queue)
        if self.io_run:
            self.io_terminated_q(queue)

    proc.n_process += 1
    self.running = False

    self.time += 1
    self.increment_wait_times(queue)
    tmp = self.taus[chr(proc.id)]
    key = chr(proc.id)
    tau = self.taus[key] * (1 - self.alpha) + proc.get_cpu_pre_time() * self.alpha
    self.taus[key] = ceil(tau)

    bursts_to_go = proc.cpu_burst_count - proc.n_process
    burst_word = "burst" if bursts_to_go == 1 else "bursts"

    if flag:
        print(f"time {self.time}ms: Process {key} (tau {tmp}ms) completed a CPU burst; {bursts_to_go} {burst_word} to go {queue_status}")
        print(f"time {self.time}ms: Recalculating tau for process {key}: old tau {tmp}ms ==> new tau {self.taus[key]}ms {queue_status}")

    if proc.get_num_proc() >= proc.cpu_burst_count:
        self.total_wait += proc.wait_time
        if proc.cpu_bound == 1:
            self.cpu_wait_time += proc.wait_time

        termination_message = f"time {self.time}ms: Process {key} terminated {queue_status}"
        print(termination_message)

        self.io_terminated_q(queue)
        self.context_switch_add(queue, proc)

  def io_buffer(self,input_of_time,queue,proc):
    self.io_run = True
    temp_time = copy.deepcopy(self.time)
    flag = self.time < 10000
    if flag:
      if(len(queue) != 0):
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q {}]".format(temp_time,chr(proc.get_id()),self.time+input_of_time+self.time_context_switch//2,' '.join(self.queue_to_string(queue))))
      else:
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q <empty>]".format(temp_time,chr(proc.get_id()),self.time+input_of_time+self.time_context_switch//2))
        
    self.arrival_checker(queue)
    self.io_terminated_q(queue)
    self.context_switch_add(queue,proc)
    self.io_run = True
    io_run_to = int(self.time + input_of_time)
    self.inoutprocess.append([proc,io_run_to])
    self.inoutprocess.sort(key = lambda x:x[1])

  def io_terminated_q(self,queue):
    checks1 = 0
    self.inoutprocess.sort(key = lambda x:[x[1],x[0].get_id()])
    while_it = 0
    if(len(self.inoutprocess)!= 0):
      while(while_it < len(self.inoutprocess)):
        if(self.time == self.inoutprocess[while_it][1]):
          checks1 = 1
          tmp = self.taus[chr((self.inoutprocess[while_it][0]).id)]
          x = 0
          while x <len(queue):
            if(tmp < self.taus[chr(queue[x].id)]):
              break
            if (tmp == self.taus[chr(queue[x].id)]):
              if (self.inoutprocess[while_it][0]).id < queue[x].id:
                break
            x += 1
            
          queue.insert(x,self.inoutprocess[while_it][0])
          self.io_complete.append(self.inoutprocess[while_it][0].get_id())
          flag = self.time < 10000
          if flag :
            print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue [Q {}]"\
            .format(self.time,chr(self.inoutprocess[while_it][0].get_id()),self.taus[chr((self.inoutprocess[while_it][0]).id)],' '.join(self.queue_to_string(queue))))
          self.inoutprocess.pop(while_it)
          while_it = 0
          if(len(self.inoutprocess) == 0):
            self.io_run = False
        else:
          while_it +=1

    if(checks1 != 1):
      return False
    else:
      return True

  def time_slice_flag(self,queue,input_of_time):
    check = input_of_time <= self.time_slice
    if(check):
      return not check
    return not check

  def algorithm_terminated_flag(self,queue):
    for process in queue:
      temp = process.check_end()
      if(temp == False):
        return temp
    return True

  def temp_output(self):
    count_total_burst_time = sum(sum(process.cpu_burst_array) for process in self.processList)
    count_total_io_time = sum(sum(process.io_bound_array) for process in self.processList)
    count_total_cpu = sum(sum(process.cpu_array) for process in self.processList)

    count_burst = sum(len(process.cpu_burst_array) for process in self.processList)
    count_io = sum(len(process.io_bound_array) for process in self.processList)
    count_cpu = sum(len(process.cpu_array) for process in self.processList)

    temp = self.total_wait + count_total_burst_time + self.time_context_switch * (self.total_switch // 2)
    temp1 = self.cpu_wait_time + count_total_cpu + self.time_context_switch * (self.cpu_switch // 2)
    temp2 = (self.total_wait - self.cpu_wait_time) + count_total_io_time + self.time_context_switch * ((self.total_switch - self.cpu_switch) // 2)

    a = count_total_burst_time / self.time
    b = count_total_burst_time / count_burst if count_burst else 0
    e = self.total_wait / count_burst if count_burst else 0
    c = count_total_cpu / count_cpu if count_cpu else 0
    f = self.cpu_wait_time / count_cpu if count_cpu else 0
    k = temp1 / count_cpu if count_cpu else 0
    h = temp / count_burst if count_burst else 0
    d = count_total_io_time / count_io if count_io else 0
    g = (self.total_wait - self.cpu_wait_time) / count_io if count_io else 0
    L = temp2 / count_io if count_io else 0
    m, n, o = self.total_switch // 2, self.cpu_switch // 2, (self.total_switch - self.cpu_switch) // 2
    r = self.total_preempt
    s, t = 0, self.total_preempt

    return ["SJF", a, b, c, d, e, f, g, h, k, L, m, n, o, r, s, t]


  def SJF(self):
    print("time {}ms: Simulator started for {} [Q <empty>]".format(self.time,"SJF"))
    queue = []
    
    while 1 == 1:
      if(self.running == False and len(queue) != 0):
        proc = copy.deepcopy(queue[0])
        
        queue.pop(0)
        self.context_switch_zero(queue,proc)
        cpu_burst_time_temp = proc.get_cpu_time()
        io_burst_time_temp = proc.get_io_time()
        self.cpu_burst(cpu_burst_time_temp,queue,proc)
        if(io_burst_time_temp == 0):
          self.process_terminate = self.process_terminate + 1
          continue
        else:
          self.io_buffer(io_burst_time_temp,queue,proc)
          continue
      
      process_queue_length = len(queue)
      if process_queue_length == 0:
        if self.running == False:
          if self.io_run == False:
            if self.process_terminate != 0:
              break

      if(self.running == False):
        ck1 = self.arrival_checker(queue)
        if(ck1 == True):
          continue
        if(self.io_run):
          ck2 = self.io_terminated_q(queue)
          if(ck2 == True):
            continue
        self.time += 1
        self.increment_wait_times(queue)
        self.arrival_checker(queue)
        if(self.io_run):
          self.io_terminated_q(queue)

    print("time {}ms: Simulator ended for SJF [Q <empty>]".format(self.time))

class RR(object):
  def __init__(self,ctsw,data,t_cs):
    self.time = 0
    self.time_context_switch =ctsw
    self.processList = copy.deepcopy(data)
    self.running = False
    self.io_run = False
    self.inoutprocess,self.complete = [], []
    self.process_terminate = 0
    self.time_slice = t_cs
    self.cpu_switch, self.cpu_wait_time, self.preemption_in_cpu,  self.total_wait ,self.total_switch, self.total_preempt = 0,0,0,0,0,0

  def increment_wait_times(self,queue):
    for process in queue:
      process.wait_time += 1
    for i in self.complete:
      i.wait_time += 1

  def queue_to_string(self,queue):
    ret = ""
    for i in queue:
      ret += chr(i.get_id())
    return ret
  def grab_process_time(self,proc):
    if(proc.run_burst != 0):
      res = (proc.get_cpu_time() - proc.run_burst)
      return res
      
    else:
      return proc.get_cpu_time()

  def arrival_checker(self,queue):
    process_arrived = False
    for process in self.processList:
        if process.get_arr() == self.time:
            process_arrived = True
            queue.append(process)
            if self.time < 10000:
                print(f"time {self.time}ms: Process {chr(process.get_id())} arrived; added to ready queue [Q {' '.join(self.queue_to_string(queue))}]")

    return process_arrived

  def context_switch_zero(self,queue,proc):
    self.total_switch +=1
    if(proc.cpu_bound ==1):
      self.cpu_switch+=1
    res = self.time_context_switch // 2
    for i in range(res):
      self.time +=1
      self.increment_wait_times(queue)
      if(i < res - 1):
        self.arrival_checker(queue)
        self.io_terminated_q(queue) 

  def time_zero(self,queue):
    self.arrival_checker(queue)
    self.io_terminated_q(queue)

  def context_switch_add(self,queue,proc):
    if(proc.cpu_bound ==1):
      self.cpu_switch+=1
    self.total_switch +=1
    res = self.time_context_switch // 2
    for i in range(res):
      self.time +=1
      if(i == res -1):
        if(len(self.complete)!=0):
          queue.append(self.complete[0])
          self.complete.pop(0)
      self.increment_wait_times(queue)
      self.io_terminated_q(queue)
      self.arrival_checker(queue)
    if(len(self.complete) != 0):
      queue.append(self.complete[0])
      self.complete.pop(0)

  def cpu_burst(self,input_of_time,queue,proc):
    if self.time < 10000:
      queue_status = "[Q <empty>]" if not queue else f"[Q {' '.join(self.queue_to_string(queue))}]"
      burst_info = "{}ms burst".format(input_of_time) if proc.run_burst == 0 else "remaining {}ms of {}ms burst".format(input_of_time, proc.get_cpu_time())
      print(f"time {self.time}ms: Process {chr(proc.get_id())} started using the CPU for {burst_info} {queue_status}")

    self.running = True
    self.time_zero(queue)
    time_temp = min(input_of_time, self.time_slice)

    for i in range(time_temp):
        self.time += 1
        self.increment_wait_times(queue)
        proc.run_burst += 1
        if i < time_temp - 1:
            self.arrival_checker(queue)
            if self.io_run:
                self.io_terminated_q(queue)
    
    if(time_temp == self.time_slice and proc.get_cpu_time() - proc.run_burst > 0):
      if(len(queue) == 0):
        while(len(queue) == 0 and proc.get_cpu_time() -proc.run_burst > 0):
          if self.time < 10000:
            print("time {}ms: Time slice expired; no preemption because ready queue is empty [Q <empty>]".format(self.time))
          self.arrival_checker(queue)
          self.io_terminated_q(queue)
          range_4_loop = min(self.time_slice,proc.get_cpu_time() -proc.run_burst)
          other = max(self.time_slice,proc.get_cpu_time() -proc.run_burst)
          for k in range(range_4_loop):
            self.time +=1
            self.increment_wait_times(queue)
            proc.run_burst +=1
            if(k < range_4_loop -1):
              self.arrival_checker(queue)
            if(k < range_4_loop -1 and self.io_run):
              self.io_terminated_q(queue)
        if(proc.get_cpu_time() -proc.run_burst == 0):
          proc.n_process+=1
          proc.run_burst = 0
        else:
          if self.time < 10000:
            print("time {}ms: Time slice expired; preempting process {} with {}ms remaining [Q {}]"\
          .format(self.time,chr(proc.get_id()),(proc.get_cpu_time() - proc.run_burst),' '.join(self.queue_to_string(queue))))
          self.total_preempt +=1
          if(proc.cpu_bound == 1):
            self.preemption_in_cpu +=1
          div2 = self.time_context_switch//2
          self.total_wait -= div2
          if(proc.cpu_bound == 1):
            self.cpu_wait_time-= div2
          self.arrival_checker(queue)
          self.io_terminated_q(queue)
          
          self.complete.append(proc)
          self.running = False
          return False
      else:
        if(self.time < 10000):
          print("time {}ms: Time slice expired; preempting process {} with {}ms remaining [Q {}]".format(self.time,chr(proc.get_id()),(proc.get_cpu_time() - proc.run_burst),' '.join(self.queue_to_string(queue))))
        self.total_preempt +=1
        if(proc.cpu_bound == 1):
            self.preemption_in_cpu = self.preemption_in_cpu + 1
        div2 = self.time_context_switch//2
        self.total_wait -= div2
        if(proc.cpu_bound == 1):
          self.cpu_wait_time-= div2
        self.arrival_checker(queue)
        self.io_terminated_q(queue)
        self.complete.append(proc)
        self.running = False
        return self.running

    else:
      proc.n_process+=1
      proc.run_burst = 0
    self.running = False

    if(proc.cpu_burst_count - proc.get_num_proc() > 0):
      if self.time < 10000:
        bursts_remaining = proc.cpu_burst_count - proc.n_process
        burst_word = "burst" if bursts_remaining == 1 else "bursts"
        queue_status = "[Q <empty>]" if not queue else f"[Q {' '.join(self.queue_to_string(queue))}]"
    
        print(f"time {self.time}ms: Process {chr(proc.get_id())} completed a CPU burst; {bursts_remaining} {burst_word} to go {queue_status}")

    else:
      self.total_wait += proc.wait_time
      if(proc.cpu_bound != 1): pass
      else: self.cpu_wait_time += proc.wait_time

      if(len(queue) != 0 ):
        print("time {}ms: Process {} terminated [Q {}]".format(self.time,chr(proc.get_id()),' '.join(self.queue_to_string(queue))))
      else:
        print("time {}ms: Process {} terminated [Q <empty>]".format(self.time,chr(proc.get_id())))
        
      self.arrival_checker(queue)
      self.io_terminated_q(queue)
      self.context_switch_add(queue,proc)

  def io_buffer(self,input_of_time,queue,proc):
    self.io_run = True
    temp_time = copy.deepcopy(self.time)
    
    flag = self.time < 10000
    if flag:
      if len(queue) == 0:
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q <empty>]".format(temp_time,chr(proc.get_id()),self.time+input_of_time+self.time_context_switch//2))
      else:
        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms [Q {}]".format(temp_time,chr(proc.get_id()),self.time+input_of_time+self.time_context_switch//2,' '.join(self.queue_to_string(queue))))

    self.arrival_checker(queue)
    self.io_terminated_q(queue)
    self.context_switch_add(queue,proc)
    self.io_run = True
    self.inoutprocess.append([proc,int(self.time + input_of_time)])
    self.inoutprocess.sort(key = lambda x:x[1])

  def io_terminated_q(self,queue):
    checks1, while_it = 0, 0
    self.inoutprocess.sort(key = lambda x:[x[1],x[0].get_id()])
    inoutleng = len(self.inoutprocess)
    if(inoutleng !=  0):
      while(while_it < len(self.inoutprocess)):
        if(self.time != self.inoutprocess[while_it][1]):
          while_it +=1
        else:
          checks1 = 1
          queue.append(self.inoutprocess[while_it][0])
          flag = self.time < 10000
          if flag:
            print("time {}ms: Process {} completed I/O; added to ready queue [Q {}]".format(self.time,chr(self.inoutprocess[while_it][0].get_id()),' '.join(self.queue_to_string(queue))))
          self.inoutprocess.pop(while_it)
          while_it = 0
          if(len(self.inoutprocess) != 0): pass
          else: self.io_run = False

    temp = False
    if(checks1 != 1):
      return temp
    else:
      return not temp

  def temp_output(self):
    count_total_burst_time = sum(sum(p.cpu_burst_array) for p in self.processList)
    count_total_io_time = sum(sum(p.io_bound_array) for p in self.processList)
    count_total_cpu = sum(sum(p.cpu_array) for p in self.processList)

    count_burst = sum(len(p.cpu_burst_array) for p in self.processList)
    count_io = sum(len(p.io_bound_array) for p in self.processList)
    count_cpu = sum(len(p.cpu_array) for p in self.processList)

    temp = self.total_wait + count_total_burst_time + self.time_context_switch * (self.total_switch // 2)
    temp1 = self.cpu_wait_time + count_total_cpu + self.time_context_switch * (self.cpu_switch // 2)
    temp2 = (self.total_wait - self.cpu_wait_time) + count_total_io_time + self.time_context_switch * ((self.total_switch - self.cpu_switch) // 2)

    def mutex(numerator, denominator):
        return numerator / denominator if denominator else 0

    a = mutex(count_total_burst_time, self.time)
    b = mutex(count_total_burst_time, count_burst)
    c = mutex(count_total_cpu, count_cpu)
    d = mutex(count_total_io_time, count_io)
    e = mutex(self.total_wait, count_burst)
    f = mutex(self.cpu_wait_time, count_cpu)
    g = mutex(self.total_wait - self.cpu_wait_time, count_io)
    h = mutex(temp, count_burst)
    k = mutex(temp1, count_cpu)
    L = mutex(temp2, count_io)
    m, n, o = self.total_switch // 2, self.cpu_switch // 2, (self.total_switch - self.cpu_switch) // 2
    r, s, t = self.total_preempt, self.preemption_in_cpu, self.total_preempt - self.preemption_in_cpu

    return ["RR", a, b, c, d, e, f, g, h, k, L, m, n, o, r, s, t]


  def RR(self):
    print("time {}ms: Simulator started for RR [Q <empty>]".format(self.time))
    queue = []
    while 1 == 1:
      if(self.running == False and len(queue) != 0):
        proc = copy.deepcopy(queue[0])
        queue.pop(0)
        self.context_switch_zero(queue,proc)
        cpu_burst_time_temp = self.grab_process_time(proc) 
        io_burst_time_temp = proc.get_io_time()
  
        check_io_or_not = self.cpu_burst(cpu_burst_time_temp,queue,proc)
        
        if(check_io_or_not == False):
          self.context_switch_add(queue,proc)
          continue

        if(io_burst_time_temp == 0):
          self.process_terminate += 1
          continue
        else:
          self.io_buffer(io_burst_time_temp,queue,proc)
          continue
        
      if(len(queue) == 0):
        if self.running == False:
          if self.io_run == False:
            if self.process_terminate != 0:
              break

      if(self.running == False):
        ck1 = self.arrival_checker(queue)
        if(ck1 == True):
          continue
        if(self.io_run):
          ck2 = self.io_terminated_q(queue)
          if(ck2 == True):
            continue
        self.time +=1
        self.increment_wait_times(queue)
        self.arrival_checker(queue)
        if(self.io_run):
          self.io_terminated_q(queue)
    print("time {}ms: Simulator ended for RR [Q <empty>]".format(self.time))

def simout_print(f, out1 ,out2,out3,out4):
  f.write("Algorithm {}\n\
-- CPU utilization: {:.3f}%\n\
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- number of context switches: {} ({}/{})\n\
-- number of preemptions: {} ({}/{})\n".format(out1[0],result_out(out1[1]*100),\
  result_out(out1[2]),result_out(out1[3]),result_out(out1[4]),\
  result_out(out1[5]),result_out(out1[6]),result_out(out1[7]),\
  result_out(out1[8]),result_out(out1[9]),result_out(out1[10]),\
    out1[11],out1[12],out1[13],\
    out1[14],out1[15],out1[16]\
    ))
  f.write("\n")
  f.write("Algorithm {}\n\
-- CPU utilization: {:.3f}%\n\
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- number of context switches: {} ({}/{})\n\
-- number of preemptions: {} ({}/{})\n".format(out2[0],result_out(out2[1]*100),\
  result_out(out2[2]),result_out(out2[3]),result_out(out2[4]),\
  result_out(out2[5]),result_out(out2[6]),result_out(out2[7]),\
  result_out(out2[8]),result_out(out2[9]),result_out(out2[10]),\
    out2[11],out2[12],out2[13],\
    out2[14],out2[15],out2[16]\
    ))
  f.write("\n")
  f.write("Algorithm {}\n\
-- CPU utilization: {:.3f}%\n\
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- number of context switches: {} ({}/{})\n\
-- number of preemptions: {} ({}/{})\n".format(out3[0],result_out(out3[1]*100),\
  result_out(out3[2]),result_out(out3[3]),result_out(out3[4]),\
  result_out(out3[5]),result_out(out3[6]),result_out(out3[7]),\
  result_out(out3[8]),result_out(out3[9]),result_out(out3[10]),\
    out3[11],out3[12],out3[13],\
    out3[14],out3[15],out3[16]\
    ))
  
  f.write("\n")
  f.write("Algorithm {}\n\
-- CPU utilization: {:.3f}%\n\
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n\
-- number of context switches: {} ({}/{})\n\
-- number of preemptions: {} ({}/{})\n".format(out4[0],result_out(out4[1]*100),\
  result_out(out4[2]),result_out(out4[3]),result_out(out4[4]),\
  result_out(out4[5]),result_out(out4[6]),result_out(out4[7]),\
  result_out(out4[8]),result_out(out4[9]),result_out(out4[10]),\
    out4[11],out4[12],out4[13],\
    out4[14],out4[15],out4[16]\
    ))
  f.close()


def main():
  f = open("simout.txt","w")

  if(len(sys.argv) != 9):
    print("Of the format: python3 project.py  3 1 1024 0.001 3000 4 0.75 256")
    sys.exit()
  
  num_proc_id = int(sys.argv[1])
  num_cpu_bound = int(sys.argv[2])
  seed = int(sys.argv[3])
  in_lambda = float(sys.argv[4])
  up_bound = int(sys.argv[5])
  time_context_switch = int(sys.argv[6])
  alpha = float(sys.argv[7])
  time_slics = int(sys.argv[8])
  
  rand48 = RandomGenerator48(seed)
  rand48.srand(seed)
  cpu = 0
  out = "process"
  if(num_cpu_bound>1):
    out="processes"
  print("<<< PROJECT PART I -- process set (n={}) with {} CPU-bound {} >>>".format(num_proc_id,num_cpu_bound,out))
  cpu_t_predict = 1/in_lambda
  list_process = []
  
  for i in range(int(num_proc_id)):
    arrival_time = math.floor(rand(rand48,in_lambda,up_bound))
    cpu_burst_count = math.ceil(rand48.drand()*64)
    pid = i
    if(num_proc_id-i==num_cpu_bound):
      cpu = 1
    parameters = [pid,arrival_time,cpu_burst_count,int(cpu_t_predict),in_lambda,rand48,up_bound,cpu]
    process = Process(parameters)
    list_process.append(process)
 
  list_process = sorted(list_process, key=operator.attrgetter('arrival_time'))
  print()
  print("<<< PROJECT PART II -- t_cs={}ms; alpha={:.2f}; t_slice={}ms >>>".format(time_context_switch,alpha,time_slics))

  cpu1 = FCFS(time_context_switch,list_process,time_slics)
  cpu1.FCFS()
  out1 = cpu1.temp_output()
  print()
  
  cpu2 = SJF(time_context_switch,list_process,time_slics,alpha)
  cpu2.SJF()
  out2 = cpu2.temp_output()
  print()
  cpu3 = SRT1(time_context_switch,list_process,time_slics,alpha)
  cpu3.SRT()
  out3 = cpu3.temp_output()

  print()
  cpu4 = RR(time_context_switch,list_process,time_slics)
  cpu4.RR()
  out4 = cpu4.temp_output()
 
  simout_print(f,out1,out2,out3,out4)

main()




















