import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

#READ IN DATA
spread          = pd.read_csv('spread.csv')
print spread[:50]

def mkplt(x,sp1,sp2,sp3,y_name):
    ax = plt.subplot(sp1,sp2,sp3)
    xgrid = [0,1,2,3,4]
    k = 0 
    for item, row in x.iterrows():
        if k % 100 == 0:
            plt.plot(row, '-b', linewidth=0.1)
            plt.ylabel(y_name,fontsize=18)
        k += 1

fig3 = plt.figure()
mkplt(spread[['y1','y2','y3','y4','y5']],2,1,1,r'$author$')
#mkplt(spread[['dy1','dy2','dy3','dy4','dy5']],2,1,2,r'$dep$')
plt.savefig('sim_plots_lat.png',bbox_inches=0)
plt.show()
