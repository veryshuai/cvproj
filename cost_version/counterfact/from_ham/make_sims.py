import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

#READ IN DATA
spread          = pd.read_csv('spread0.csv')

def mkplt(x,sp1,sp2,sp3,y_name,inc_dat=False,tot=0,xlab=''):
    ax = plt.subplot(sp1,sp2,sp3)
    xgrid = [0,1,2,3,4]
    k = 0 
    for item, row in x.iterrows():
        plt.plot(row, '-b', linewidth=0.05)
        plt.ylabel(y_name,fontsize=12)
        # plt.plot(row, '-b', linewidth=0.07)
        # plt.ylabel(y_name,fontsize=12)
        # plt.plot(row, '-b', linewidth=0.1)
        # plt.ylabel(y_name,fontsize=12)
        k += 1
    plt.xlabel(xlab,fontsize=12)
    if inc_dat:
        if tot == 1:
            dat = plt.plot([0.0068337129840546698,
                            0.0091116173120728925,
                            0.015945330296127564,
                            0.020501138952164009,
                            0.025056947608200455,
                            0.027334851936218679] , '-k', linewidth=2)
        if tot == 0:  
            dat = plt.plot([0, 0.013043478260869565, 0.086956521739130432,
                      0.14782608695652175, 0.24782608695652175,
                      0.34347826086956523], '-k', linewidth=2)
        if tot == 2:
            dat = plt.plot([0.028846153846153848,
                            0.20192307692307693,
                            0.26923076923076922,
                            0.35576923076923078,
                            0.42307692307692307,
                            0.49038461538461536], '-k', linewidth=2)
            # plt.ylim([0,0.4])
        if tot == 3:
            dat = plt.plot([0.014208425594185285,
                            0.022564292366305118,
                            0.028046086930657976,
                            0.031212071828248138,
                            0.028881737442541133,
                            0.032424673992380713], '-k', linewidth=2)

fig3 = plt.figure()
mkplt(spread[['cf0','cf1','cf2','cf3','cf4','cf5']],3,1,1,r'% authors', True, 1)
mkplt(spread[['df0','df1','df2','df3','df4','df5']],3,1,2,r'% departments', True, 2)
mkplt(spread[['sd0','sd1','sd2','sd3','sd4','sd5']],3,1,3,r'department std. dev.', True, 3, r'years since publication')
plt.savefig('sim_plots_lat.png',bbox_inches=0)
plt.show()

