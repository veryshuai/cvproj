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

    alp = [-1.2449938399200924,0.30439991322583293]
    gam = [0.027582629753577594,0.067002307925056154]
    bet = [0.035266021805193302]
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'field': 0.56104025904547605, 'qual': 0.42062703573608634, 'lat': 1.2837487696003824})
    
    # OTHER PARAMETERS 
    lo = 11.374821450184788 #offer arrival rate,
    ip = 0.45356716416109194 #instrument parameter (affects 1991 wages)
    # two mean parameters and a standard deviation
    lp = [-1.3808013227699647,-5.170318982125627,0.55080237964410705] #latent type probability,
    # base and qual dependence
    p = 0 # 1.282008407975466 #signing bonus distribution parameter
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
