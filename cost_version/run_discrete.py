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

    alp = [-2.6202663774184853,0.47442395115292668,-0.044248508487238589,0.33027299490174994,-0.0030644546916960601]
    gam = [0.76657686859417083]
    bet = [0.106882393702329698]
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'field': 0.087542212166186101, 'qual': 0.54006378260352617, 'lat': 0.1500699285997715})
    
    # OTHER PARAMETERS 
    lo = 9 #offer arrival rate,
    ip = 2.4208818655880147 #instrument parameter (affects 1991 wages)
    # two mean parameters and a standard deviation
    lp = [-0.4,0.1] #latent type probability,
    # base and qual dependence
    p = 0 # 1.282008407975466 #signing bonus distribution parameter
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
