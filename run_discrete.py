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

    alp = [-1.6912994607298211,0.00074314419443021374]
    bet = 10.829271047737196
    gam = [0.034228248703075864,0.098392799712779644]
    
    # INITIAL MOV PARAMETERS 
    mov_params = pd.Series({'qual': 0.46218713564513042, 'field': -1.8773030907893029, 'lat': -0.26855264979563331})
    
    # OTHER PARAMETERS 
    lp = [-26.251278310241567,61.02761089372683,1.0325140952129204] #latent type probability,
    # two mean parameters and a standard deviation
    lo = [0.016572481018500451,0.040909561164198333]  #offer arrival rate,
    # base and qual dependence
    p = 1.282008407975466 #signing bonus distribution parameter
    ip = 4.044689899777988 #instrument parameter (affects 1991 wages)
    
    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]
    
    d.main(cit_params, big_mov_params, lp, ip)
