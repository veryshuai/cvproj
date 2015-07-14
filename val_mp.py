# My first attempt to calculate the value function 
# in multiple processers

import multiprocessing
import time
import val_defs as vd
import cit_defs as cd
import collections
import pickle
import math
import pandas as pd

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
                 ds, d, ip, bd, init, lp):
        self.q = q
        self.f = f
        self.l = l
        self.bmp = bmp
        self.ds = ds
        self.d = d
        self.init = init
        self.ip = ip
        self.bd = bd
        self.lp = lp
    def __call__(self):
        val, trans, itrans = val_calc(self.q, self.f, self.l,
                              self.bmp, self.ds, self.d,
                              self.ip, self.bd,
                              self.init, self.lp)
        return [self.q, self.f, self.l, val, trans, itrans]
    def __str__(self):
        return 'q %s, f %s, l %s ' % (self.q, self.f, self.l)

class Task_mlik(object):
    def __init__(self, n9, is9, trans, itrans, lat):
        self.n9 = n9 
        self.is9 = is9 
        self.trans = trans 
        self.itrans = itrans 
        self.lat = lat 
    def __call__(self):
        together = mlik_calc(self.n9, self.is9,
                              self.trans, self.itrans,
                              self.lat)
        return [self.lat, together]
    def __str__(self):
        return 'l %s ' % (self.lat)


def call_parallel(big_mov_params, dep_stats, dis,
                  ip, bd, init, lp, mov_dat_not91,
                  mov_dat91):
    """Calls parallel loop for calculating value function"""

    # Establish communication queues
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    
    # Start consumers
    num_consumers = 16 
    consumers = [ Consumer(tasks, results)
                  for i in xrange(num_consumers) ]
    for w in consumers:
        w.start()
    
    #PART 1: VAL AND TRANS
    # Enqueue jobs
    for q in range(2):
        for f in range(2):
            for l in range(4):
                tasks.put(Task(q, f, l, big_mov_params,
                               dep_stats, dis,
                               ip, bd, init, lp))
    
    # Add a poison pill for each consumer
    for i in xrange(num_consumers):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()

    # Start printing results
    vals = tree()
    trans = tree()
    itrans = tree()
    num_jobs = 16
    while num_jobs:
        r = results.get()
        vals[r[0]][r[1]][r[2]]   = r[3]
        trans[r[0]][r[1]][r[2]]  = r[4]
        itrans[r[0]][r[1]][r[2]] = r[5]
        num_jobs -= 1

    mlik = mlik_part(mov_dat_not91, mov_dat91,
              trans, itrans)

    return vals, trans, itrans, mlik


def mlik_part(mov_dat_not91, mov_dat91,
              trans, itrans):
    """ This does the mlik parallel part"""

    # Establish communication queues
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    
    # Start consumers
    num_consumers = 4
    consumers = [ Consumer(tasks, results)
                  for i in xrange(num_consumers) ]
    for w in consumers:
        w.start()

    # Enqueue jobs for mlik part
    for l in range(4):
        tasks.put(Task_mlik(mov_dat_not91, mov_dat91,
                            trans, itrans, l))

    # Add a poison pill for each consumer
    for i in xrange(num_consumers):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()

    # Start printing results
    mlik = [0,0,0,0]
    num_jobs = 4
    while num_jobs:
        r = results.get()
        mlik[r[0]]   = r[1] 
        num_jobs -= 1

    return mlik

def from_pickle(arg=0):
    """reads in vals and trans from pickle"""
    vals = pd.read_pickle('val_init.pickle')
    trans = pd.read_pickle('trans.pickle')
    itrans = pd.read_pickle('itrans.pickle')
    mlik = pd.read_pickle('mlik.pickle')
    # f = file('trans.pickle','rb'); trans = pickle.load(f)
    # f.close()
    # f = file('itrans.pickle','rb'); itrans = pickle.load(f)
    # f.close()
    # f = file('mlik.pickle','rb'); mlik = pickle.load(f)
    if arg == 0:
        return vals, trans, trans
    if arg == 1:
        return mlik

def val_calc(qual, field, lat, big_mov_params,
             dep_stats, dis, ip, bd, init, lp):
    """calculates a single value function"""

    # UNPACK
    [mov_params, lam, p] = big_mov_params
    
    # QUADRATURE POINTS 
    qa = [4 * math.sqrt(3 - 2 * math.sqrt(6 / float(5))) / float(7),
            4 * math.sqrt(3 + 2 * math.sqrt(6 / float(5))) / float(7)]
    qp =  [-qa[1], -qa[0], qa[0], qa[1]]

    # CALCULATE WAGES
    wage = vd.calc_wage(mov_params, dep_stats,
                     qual, field, lat, qp)
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
            vals, trans, itrans = from_pickle(0)
    return vals, trans, itrans

def mlik_calc(mov_dat_not91, mov_dat91, trans, itrans, lat):
    try:
        not91 = mov_dat_not91.groupby('au').apply(lambda x:
                cd.mov_lik(trans, x, lat))
        is91  = mov_dat91.groupby('au').apply(lambda x:
                cd.mov_lik(itrans, x, lat))
        together = pd.DataFrame({'not91': not91,
            'is91': is91}, index=not91.index)
        together = together.fillna(value=1)
        together = together.prod(1)
        return together
    except Exception as e:
        print e
        print 'WARNING: reading mlik from save'
        mlik = from_pickle(1)
        return mlik[0]

