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

    alp = [-0.58682250047630902]
    gam = [0.033100621081977047,0.10087651831582922]
    bet = [17.960785941454546]
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'field': 0.93208506111690093, 'qual': 1.9, 'lat': 2.5})
    
    # OTHER PARAMETERS 
    lo = 8.5 #offer arrival rate,
    ip = 3.5 #instrument parameter (affects 1991 wages)
    # two mean parameters and a standard deviation
    lp = [-1,-8,0.5] #latent type probability,
    # base and qual dependence
    p = 0 # 1.282008407975466 #signing bonus distribution parameter
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
