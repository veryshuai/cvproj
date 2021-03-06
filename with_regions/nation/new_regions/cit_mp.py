# My first attempt to calculate the value function 
# in multiple processers

import multiprocessing
import time
import cit_defs as cd
import collections
import pickle
import numpy as np
import math

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
    def __init__(self, cp, dy, dr, dn, l, lp,
             c, fc, nc):
        self.cp = cp
        self.dy = dy 
        self.dr = dr 
        self.dn = dn 
        self.l = l
        self.lp = lp 
        self.c = c 
        self.fc = fc 
        self.nc = nc 
    def __call__(self):
        cl_res, fc_res, nc_res =\
                cit_calc(self.cp, self.dy, self.dr, self.dn,
                         self.l, self.lp, self.c, self.fc,
                         self.nc)
        return self.l, cl_res, fc_res, nc_res
    def __str__(self):
        return 'l %s ' % (self.l)


def call_parallel(cit_params, dep_year, dep_reg, dep_nat, lp,
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
        tasks.put(Task(cit_params, dep_year, dep_reg, dep_nat, l, lp,
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

def cit_calc(cit_params, dep_year, dep_reg, dep_nat, lat, lp,
             citers, first_cits, nocits):
    """calculates a single lat type cit likelihood"""

    # UNPACK
    [alp, gam, bet] = cit_params

    # QUADRATURE POINTS 
    qa = [4 * math.sqrt(3 - 2 * math.sqrt(6 / float(5))) / float(7),
            4 * math.sqrt(3 + 2 * math.sqrt(6 / float(5))) / float(7)]
    qp =  [-qa[1], -qa[0], qa[0], qa[1]]

    try: 
        cl_res = citers.groupby('au')\
                    .apply(lambda x: cd.cit_lik_cit(alp,
                           bet, gam, x, dep_year, dep_reg, dep_nat, lat, qp))
        fc_res = first_cits.groupby('au')\
                    .apply(lambda x: cd.fc_lik(alp,
                           bet, gam,  x, dep_year, dep_reg, dep_nat, lat, qp))
        nc_res = nocits.groupby('au')\
                    .apply(lambda x: cd.cit_lik_no_cit(alp,
                           bet, gam, x, dep_year, dep_reg, dep_nat, lat, qp))
    except Exception as e:
        print 'WARNING: Error in cit_lik calc, cit_mp.py' 
        print e
        cl_res, fc_res, nc_res = 1e-200, 1e-200, 1e-200,
    return cl_res, fc_res, nc_res

