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

    alp = -1.6749907947388878
    bet = 10.102329748914448
    gam = [0.04046044427069205,0.3]
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'qual': 1, 'field': -1.6987073884478081, 'lat': 1})
    
    # OTHER PARAMETERS 
    lp = [0, 1, 1] #latent type probability,
    # two mean parameters and a standard deviation
    lo = [0.038882490293258982, 0.01]  #offer arrival rate,
    # base and qual dependence
    p = 1.3625786095456844 #signing bonus distribution parameter
    ip = 1 #instrument parameter (affects 1991 wages)
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
