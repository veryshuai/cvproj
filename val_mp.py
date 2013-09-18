# My first attempt to calculate the value function 
# in multiple processers

import multiprocessing
import time
import val_defs as vd
import collections
import pickle

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
    def __init__(self, q, f, l, bmp,
                 ds, d, ip, bd, init):
        self.q = q
        self.f = f
        self.l = l
        self.bmp = bmp
        self.ds = ds
        self.d = d
        self.init = init
        self.ip = ip
        self.bd = bd
    def __call__(self):
        val, trans, itrans = val_calc(self.q, self.f, self.l,
                              self.bmp, self.ds, self.d,
                              self.ip, self.bd, self.init)
        return [self.q, self.f, self.l, val, trans, itrans]
    def __str__(self):
        return 'q %s, f %s, l %s ' % (self.q, self.f, self.l)


def call_parallel(big_mov_params, dep_stats, dis, ip, bd, init=[]):
    """Calls parallel loop for calculating value function"""

    # Establish communication queues
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    
    # Start consumers
    num_consumers = 3
    consumers = [ Consumer(tasks, results)
                  for i in xrange(num_consumers) ]
    for w in consumers:
        w.start()
    
    # Enqueue jobs
    for q in range(3):
        for f in range(2):
            for l in range(2):
                tasks.put(Task(q, f, l, big_mov_params,
                               dep_stats, dis,
                               ip, bd, init))
    
    # Add a poison pill for each consumer
    for i in xrange(num_consumers):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()
    
    # Start printing results
    vals = tree()
    trans = tree()
    itrans = tree()
    num_jobs = 12
    while num_jobs:
        r = results.get()
        vals[r[0]][r[1]][r[2]]   = r[3]
        trans[r[0]][r[1]][r[2]]  = r[4]
        itrans[r[0]][r[1]][r[2]] = r[5]
        num_jobs -= 1
    return vals, trans, itrans

def from_pickle():
    """reads in vals and trans from pickle"""
    f = file('trans.pickle','rb')
    trans = pickle.load(f)
    f.close()
    f = file('val_init.pickle','rb')
    vals = pickle.load(f)
    f.close()
    return vals, trans, trans

def val_calc(qual, field, lat, big_mov_params,
             dep_stats, dis, ip, bd, init=[]):
    """calculates a single value function"""
    [mov_params, lam, p] = big_mov_params
    wage = vd.calc_wage(mov_params, dep_stats,
                     qual, field, lat)
    try:
        sp = init[qual][field][lat]
        vals, trans, itrans = vd.val_loop(wage, lam, dis,
                                  p, ip, bd, sp)
    except Exception as e:
        print 'WARNING: Value function start point error,\
                 file val_defs.py, function val_init'
        print e
        try:
            vals, trans, itrans = vd.val_loop(wage, lam, dis,
                                      p, ip, bd)
        except Exception as e:
            print 'WARNING: reading vals and trans from saves'
            print e
            vals, trans, itrans = from_pickle()
    return vals, trans, itrans

