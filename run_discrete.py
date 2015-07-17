# This script reads in parameters and runs discrete.py

import collections
import discrete as d
import pandas as pd

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

if __name__ == '__main__':
    """reads in parameters and calls discrete.py, main estimation"""

    alp = [-0.85935316208593582]
    bet = [24.413909243209535]
    gam = [0.033959685541711818,0.13384657613216921]
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'qual': 0.65969957496543075, 'field': 1.2001130355780396, 'lat': -0.73023384600604879})
    
    # OTHER PARAMETERS 
    lp = [-1.583948563522001,-1.9036011673316251,0.52782901469976462] #latent type probability,
    # two mean parameters and a standard deviation
    lo = 8.3130992669483863  #offer arrival rate,
    # base and qual dependence
    p = 0# 1.282008407975466 #signing bonus distribution parameter
    ip = 4.079568109797127 #instrument parameter (affects 1991 wages)
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
