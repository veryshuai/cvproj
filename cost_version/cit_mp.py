# My first attempt to calculate the value function 
# in multiple processers

import multiprocessing
import time
import cit_defs as cd
import collections
import pickle
import numpy as np
import math
import logging

#BASIC DEBUG LOG CONFIGURATION
logging.basicConfig(level=logging.DEBUG)

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

class Consumer(multiprocessing.Process):
    
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                self.task_queue.task_done()
                break
            answer = next_task()
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return


class Task(object):
    def __init__(self, cp, l, lp,
             c, fc, nc):
        self.cp = cp
        self.l = l
        self.lp = lp 
        self.c = c 
        self.fc = fc 
        self.nc = nc 
    def __call__(self):
        cl_res, fc_res, nc_res =\
                cit_calc(self.cp,  self.l,
                         self.lp, self.c, self.fc,
                         self.nc)
        return self.l, cl_res, fc_res, nc_res
    def __str__(self):
        return 'l %s ' % (self.l)


def call_parallel(cit_params,  lp,
             citers, first_cits, nocits):
    """Calls parallel loop for calculating value function"""

    # Establish communication queues
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    
    # Start consumers
    num_consumers = 4
    consumers = [ Consumer(tasks, results)
                  for i in xrange(num_consumers) ]
    for w in consumers:
        w.start()
    
    # Enqueue jobs
    for l in range(4):
        tasks.put(Task(cit_params, l, lp,
             citers, first_cits, nocits))
    
    # Add a poison pill for each consumer
    for i in xrange(num_consumers):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()
    
    # Start printing results
    cit_liks, fc_liks, nocit_liks\
            = [0,0,0,0], [0,0,0,0], [0,0,0,0]
    num_jobs = 4
    while num_jobs:
        r = results.get()
        cit_liks[r[0]]   = r[1] 
        fc_liks[r[0]]    = r[2]
        nocit_liks[r[0]] = r[3]
        num_jobs -= 1
        
    return cit_liks, fc_liks, nocit_liks

def cit_calc(cit_params,  lat, lp,
             citers, first_cits, nocits):
    """calculates a single lat type cit likelihood"""

    # UNPACK
    [alp, gam, bet] = cit_params

    # QUADRATURE POINTS 
    # Gauss Hermite Integration quadrature points 
    qp = [[],[]]
    qp[0] = [math.sqrt(2) * lp[1] * elem for elem in [-1.65068,-0.524648,0.524648,1.65068]]
    qp[1] = [math.sqrt(2) * lp[1] * elem + lp[0] for elem in [-1.65068,-0.524648,0.524648,1.65068]] #high first field

    try: 
        cl_res = citers.groupby('au')\
                    .apply(lambda x: cd.cit_lik_cit(alp,
                           bet, gam, x,  lat, qp))
        fc_res = first_cits.groupby('au')\
                    .apply(lambda x: cd.fc_lik(alp,
                           bet, gam,  x,  lat, qp))
        nc_res = nocits.groupby('au')\
                    .apply(lambda x: cd.cit_lik_no_cit(alp,
                           bet, gam, x,  lat, qp))
    except Exception as e:
        print 'WARNING: Error in cit_lik calc, cit_mp.py' 
        print e
        logging.exception("Something awful happened!")
        cl_res, fc_res, nc_res = 1e-200, 1e-200, 1e-200,
    return cl_res, fc_res, nc_res

