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

    alp = [-0.56945452531275809]
    bet = [15.602400261243089]
    gam = [0.038372248406727365,0.079477727422792799]
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'qual': 0.27344725062483821, 'field': 1.1834150397048537, 'lat': -1.0034251581340474})
    
    # OTHER PARAMETERS 
    lp = [-1.5470558565886836,-1.0702211065628657,0.36723437029046224] #latent type probability,
    # two mean parameters and a standard deviation
    lo = 8.3066733345055646 #offer arrival rate,
    # base and qual dependence
    p = 0 # 1.282008407975466 #signing bonus distribution parameter
    ip = 4.0413296516360013 #instrument parameter (affects 1991 wages)
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
