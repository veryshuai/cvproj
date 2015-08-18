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
    bet = [17.960785941454546,80,0]
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'field': -1.7995155486991625, 'qual': 1.9170889488351979, 'lat': 2.3190487281868641})
    
    # OTHER PARAMETERS 
    lo = 12.164206478197812 #offer arrival rate,
    ip = 0.18491156401697689 #instrument parameter (affects 1991 wages)
    # two mean parameters and a standard deviation
    lp = [-1.3273956579724473,-7.5836621981938714,0.49420258156356101] #latent type probability,
    # base and qual dependence
    p = 0 # 1.282008407975466 #signing bonus distribution parameter
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
