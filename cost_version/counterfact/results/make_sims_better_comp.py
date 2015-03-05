import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import math

#READ IN DATA
spread0          = pd.read_csv('spread0.csv')
spread1          = pd.read_csv('spread1.csv')
spread2          = pd.read_csv('spread2.csv')
#  spread3          = pd.read_csv('spread3.csv')

def mkplt(x,sp1,sp2,sp3,y_name,col='-b',inc_dat=False,tot=False):
    ax = plt.subplot(sp1,sp2,sp3)
    xgrid = [1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999]
    means = []
    twentyfive = []
    seventyfive = []
    stderr = []
    meds = []
    for name in x.columns:
        des = x[name].describe()
        means.append(des['mean'])
        twentyfive.append(x[name].quantile(q=0.25))
        seventyfive.append(x[name].quantile(q=0.75))
        meds.append(x[name].quantile(q=0.5))
        stderr.append(1.65 * des['std'] / math.sqrt(x[name].count()))
    mean_plt = plt.plot(means, "".join(['-',col]), linewidth=2)
    # med_plt = plt.plot(meds,"".join(['-',col]), linewidth=1, color='r')
    med_plt = []
    #plt.plot(twentyfive, "".join(['--',col]), linewidth=0.3)
    #plt.plot(seventyfive,"".join(['--',col]), linewidth=0.3)
    plt.plot([i - j for i, j in zip(means,stderr)],"".join(['-.',col]), linewidth=0.3)
    plt.plot([i + j for i, j in zip(means,stderr)],"".join(['-.',col]), linewidth=0.3)
    plt.title(y_name, fontsize=14);
    ax.set_xticklabels(range(1987,1999))

    print stderr
    
    dat = []
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
    return means, mean_plt, med_plt, dat

fig1 = plt.figure(figsize=(17,  8),  dpi=80)
m0, mean0, med0, dat = mkplt(spread0[['cf0','cf1','cf2','cf3','cf4','cf5','cf6','cf7','cf8','cf9','cf10','cf11','cf12']],1,3,1,r'% authors','b',False,1)
m1, mean1, med1, dat = mkplt(spread1[['cf0','cf1','cf2','cf3','cf4','cf5','cf6','cf7','cf8','cf9','cf10','cf11','cf12']],1,3,1,r'% authors','r',False,1)
m2, mean2, med2, dat = mkplt(spread2[['cf0','cf1','cf2','cf3','cf4','cf5','cf6','cf7','cf8','cf9','cf10','cf11','cf12']],1,3,1,r'% authors','y',False,1)
lgd = plt.legend([mean0[0], mean1[0], mean2[0]], ['half', 'data', 'double'], 4)
#plt.savefig('sim_plots_cf_cf.png',bbox_inches=0)

# fig5 = plt.figure(figsize=(17,  8),  dpi=80)
m0, mean0, med0, dat = mkplt(spread0[['df0','df1','df2','df3','df4','df5','df6','df7','df8','df9','df10','df11','df12']],1,3,2,r'% departments','b',False,2)
m1, mean1, med1, dat = mkplt(spread1[['df0','df1','df2','df3','df4','df5','df6','df7','df8','df9','df10','df11','df12']],1,3,2,r'% departments','r',False,2)
m2, mean2, med2, dat = mkplt(spread2[['df0','df1','df2','df3','df4','df5','df6','df7','df8','df9','df10','df11','df12']],1,3,2,r'% departments','y',False,2)
lgd = plt.legend([mean0[0], mean1[0], mean2[0]], ['half', 'data', 'double'], 4)
#lgd = plt.legend([mean0[0], med0[0], dat[0]],['mean','median','data'], 4)
# plt.savefig('sim_plots_cf_df.png',bbox_inches=0)

# fig7 = plt.figure(figsize=(17,  8),  dpi=80)
m0, mean0, med0, dat = mkplt(spread0[['cv0','cv1','cv2','cv3','cv4','cv5','cv6','cv7','cv8','cv9','cv10','cv11','cv12']],1,3,3,r'department coef var','b',False,3)
m1, mean1, med1, dat = mkplt(spread1[['cv0','cv1','cv2','cv3','cv4','cv5','cv6','cv7','cv8','cv9','cv10','cv11','cv12']],1,3,3,r'department coef var','r',False,3)
m2, mean2, med2, dat = mkplt(spread2[['cv0','cv1','cv2','cv3','cv4','cv5','cv6','cv7','cv8','cv9','cv10','cv11','cv12']],1,3,3,r'department coef var','y',False,3)
lgd = plt.legend([mean0[0], mean1[0], mean2[0]], ['half', 'data', 'double'], 1)
plt.savefig('sim_plots_cf.png',bbox_inches=0)

#    dif = spread2.applymap(math.log) - spread1.applymap(math.log)
#    
#    fig2 = plt.figure(figsize=(17,  8),  dpi=80)
#    m0, mean0, med0, dat = mkplt(dif[['df0','df1','df2','df3','df4','df5','df6']],2,3,2,r'log diff % depts (doub $\lambda_o$ - data $\lambda_o$)','b',False,1)
#    plt.plot([0,0,0,0,0,0,0],'--k')
#    #plt.savefig('sim_plots_cf_df_frac.png',bbox_inches=0)
#    
#    # fig4 = plt.figure(figsize=(17,  8),  dpi=80)
#    m0, mean0, med0, dat = mkplt(dif[['cf0','cf1','cf2','cf3','cf4','cf5','cf6']],2,3,1,r'log diff % authors (doub $\lambda_o$ - data $\lambda_o$)','b',False,1)
#    plt.plot([0,0,0,0,0,0,0],'--k')
#    #plt.savefig('sim_plots_cf_cf_frac.png',bbox_inches=0)
#    
#    # fig6 = plt.figure(figsize=(17,  8),  dpi=80)
#    m0, mean0, med0, dat = mkplt(dif[['cv0','cv1','cv2','cv3','cv4','cv5','cv6']],2,3,3,r'log diff dept cv (doub $\lambda_o$ - data $\lambda_o$)','b',False,1)
#    plt.plot([0,0,0,0,0,0,0],'--k')
#    
#    dif = spread1.applymap(math.log) - spread0.applymap(math.log)
#    
#    m0, mean0, med0, dat = mkplt(dif[['df0','df1','df2','df3','df4','df5','df6']],2,3,5,r'log diff % depts (data $\lambda_o$ - half $\lambda_o$)','b',False,1)
#    plt.plot([0,0,0,0,0,0,0],'--k')
#    #plt.savefig('sim_plots_cf_df_frac.png',bbox_inches=0)
#    
#    # fig4 = plt.figure(figsize=(17,  8),  dpi=80)
#    m0, mean0, med0, dat = mkplt(dif[['cf0','cf1','cf2','cf3','cf4','cf5','cf6']],2,3,4,r'log diff % authors (data $\lambda_o$ - half $\lambda_o$)','b',False,1)
#    plt.plot([0,0,0,0,0,0,0],'--k')
#    #plt.savefig('sim_plots_cf_cf_frac.png',bbox_inches=0)
#    
#    # fig6 = plt.figure(figsize=(17,  8),  dpi=80)
#    m0, mean0, med0, dat = mkplt(dif[['cv0','cv1','cv2','cv3','cv4','cv5','cv6']],2,3,6,r'log diff dept cv (data $\lambda_o$ - half $\lambda_o$)','b',False,1)
#    plt.plot([0,0,0,0,0,0,0],'--k')
#    plt.savefig('sim_plots_cf_frac.png',bbox_inches=0)

# fig7 = plt.figure(figsize=(17,  8),  dpi=80)
# m0, mean0, dat = mkplt(spread0[['ds0','ds1','ds2','ds3','ds4','ds5']],1,1,1,r'% departments','b',True,2)
# m1, mean1, dat = mkplt(spread1[['ds0','ds1','ds2','ds3','ds4','ds5']],1,1,1,r'% departments','r',True,2)
# m2, mean2, dat = mkplt(spread2[['ds0','ds1','ds2','ds3','ds4','ds5']],1,1,1,r'% departments','y',True,2)
# lgd = plt.legend([dat[0], mean0[0], mean1[0], mean2[0]], ['data', 'full', 'nolat', 'nolat_nobet'], 4)
# plt.savefig('sim_plots_comp_df_dat.png',bbox_inches=0)
# 
# fig8 = plt.figure(figsize=(17,  8),  dpi=80)
# m0, mean0, dat = mkplt(spread0[['dd0','dd1','dd2','dd3','dd4','dd5']],1,1,1,r'department std devs','b',True,3)
# m1, mean1, dat = mkplt(spread1[['dd0','dd1','dd2','dd3','dd4','dd5']],1,1,1,r'department std devs','r',True,3)
# m2, mean2, dat = mkplt(spread2[['dd0','dd1','dd2','dd3','dd4','dd5']],1,1,1,r'department std devs','y',True,3)
# lgd = plt.legend([dat[0], mean0[0], mean1[0], mean2[0]], ['data', 'full', 'nolat', 'nolat_nobet'], 4)
# plt.savefig('sim_plots_comp_sd_dat.png',bbox_inches=0)
plt.show()

