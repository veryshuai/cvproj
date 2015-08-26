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

    alp = [-1.452914679138346,0.384680168235423,0]
    gam = [0.026657686859417083,0.090153910685092264]
    bet = [0.05155450232934633]
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'field': 0.12716535145644681, 'qual': 0.5150051996522087, 'lat': 0.1203963289888007})
    
    # OTHER PARAMETERS 
    lo = 8.4861977159094426 #offer arrival rate,
    ip = 0.39916307819310826 #instrument parameter (affects 1991 wages)
    # two mean parameters and a standard deviation
    lp = [-1.518518796354166,-3.4449688779775971,0.54461805780012695] #latent type probability,
    # base and qual dependence
    p = 0 # 1.282008407975466 #signing bonus distribution parameter
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
