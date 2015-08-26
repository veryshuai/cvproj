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
    def __init__(self, q, f, l, hff, bmp,
                 ds, d, ip, bd, init, lp):
        self.q = q
        self.f = f
        self.l = l
        self.hff = hff
        self.bmp = bmp
        self.ds = ds
        self.d = d
        self.init = init
        self.ip = ip
        self.bd = bd
        self.lp = lp
    def __call__(self):
        val, trans, itrans, flag = val_calc(self.q, self.f, 
                              self.l, self.hff, self.bmp, self.ds, 
                              self.d, self.ip, self.bd,
                              self.init, self.lp)
        return [self.q, self.f, self.l, self.hff, val, trans, itrans, flag]
    def __str__(self):
        return 'q %s, f %s, l %s, hff %s ' % (self.q, self.f, self.l, self.hff)

class Task_mlik(object):
    def __init__(self, n9, is9, trans, itrans, lat):
        self.n9 = n9 
        self.is9 = is9 
        self.trans = trans 
        self.itrans = itrans 
        self.lat = lat 
    def __call__(self):
        together, flag = mlik_calc(self.n9, self.is9,
                              self.trans, self.itrans,
                              self.lat)
        return [self.lat, together, flag]
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
                for hff in range(2):
                    tasks.put(Task(q, f, l, hff, big_mov_params,
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
    flag = 0 #error flag
    num_jobs = 32 
    while num_jobs:
        r = results.get()
        vals[r[0]][r[1]][r[2]][r[3]]   = r[4]
        trans[r[0]][r[1]][r[2]][r[3]]  = r[5]
        itrans[r[0]][r[1]][r[2]][r[3]] = r[6]
        flag = max(flag,r[7]) #look for error flag
        num_jobs -= 1

    mlik, mflag = mlik_part(mov_dat_not91, mov_dat91,
              trans, itrans)

    flag = max(flag, mflag) #check for error in mlik calc

    return vals, trans, itrans, mlik, flag


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
    flag = 0 #Error flag
    while num_jobs:
        r = results.get()
        mlik[r[0]]   = r[1] 
        flag         = max(flag,r[2])
        num_jobs -= 1

    return mlik, flag

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
        return vals, trans, itrans
    if arg == 1:
        return mlik

def val_calc(qual, field, lat, hff, big_mov_params,
             dep_stats, dis, ip, bd, init, lp):
    """calculates a single value function"""

    # ERROR FLAG RESET
    flag = 0

    # UNPACK
    [mov_params, lam, p] = big_mov_params
    
    # QUADRATURE POINTS 
    # Gauss Hermite Integration quadrature points 
    qp = [[],[]]
    qp[0] = [math.sqrt(2) * lp[1] * elem for elem in [-1.65068,-0.524648,0.524648,1.65068]]
    qp[1] = [math.sqrt(2) * lp[1] * elem + lp[0] for elem in [-1.65068,-0.524648,0.524648,1.65068]] #high first field

    # CALCULATE WAGES
    wage = vd.calc_wage(mov_params, dep_stats,
                     qual, field, lat, hff, qp)
    try:
        #sp = init[qual][field][lat]
        sp = init[0][0][0][0]
        vals, trans, itrans = vd.val_loop(wage, lam, dis,
                                  p, ip, bd, sp)
    except Exception as e:
        # print 'WARNING: Value function start point error,\
        #          file val_defs.py, function val_init'
        # print e
        # logging.exception("Something awful happened!")
        # try:
        #     vals, trans, itrans = vd.val_loop(wage, lam, dis,
        #                               p, ip, bd)
        #     for tb in traceback.format_tb(sys.exc_info()[2]):
        #         print tb
        # except Exception as e:
        print 'WARNING: reading vals from saves, equal trans'
        print e
        
        vals, trans, itrans = from_pickle(0)
        flag = 1
    return vals, trans, itrans, flag

def mlik_calc(mov_dat_not91, mov_dat91, trans, itrans, lat):

    #Set Error Flag
    flag = 0

    try:
        not91 = mov_dat_not91.groupby('au').apply(lambda x:
                cd.mov_lik(trans, x, lat))
        is91  = mov_dat91.groupby('au').apply(lambda x:
                cd.mov_lik(itrans, x, lat))
        together = pd.DataFrame({'not91': not91,
            'is91': is91}, index=not91.index)
        together = together.fillna(value=1)
        together = together.prod(1)
        return together, flag
    except Exception as e:
        print e
        print 'WARNING: reading mlik from save'
        mlik = from_pickle(1)
        mlik[0] = mlik[0] + -1e20
        flag = 1
        return mlik[0], flag


