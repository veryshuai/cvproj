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

    alp = tree()
    gam = tree()
    bet = tree()
    
    alp[0][0][0] = -1.6749907947388878
    alp[0][1][0] = -0.023230102077945278
    gam[0][0][0] = 0.04046044427069205
    gam[0][1][0] = 0.094606140815592599
    bet[0][0][0] = 10.182637130124046
    bet[0][1][0] = 10.102329748914448
    alp[0][0][1] = 1
    alp[0][1][1] = 1 #0.1
    bet[0][0][1] = 0
    bet[0][1][1] = 0 #10
    gam[0][0][1] = 0.1
    gam[0][1][1] = 0.1 # 0.1
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'qual': -1, 'field': -1.6987073884478081, 'lat': 1})
    
    # OTHER PARAMETERS 
    lp = [-1, 1] #latent type probability
    lo = 0.058882490293258982 #offer arrival rate
    p = 1.3625786095456844 #signing bonus distribution parameter
    ip = 1 #instrument parameter (affects 1991 wages)
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
