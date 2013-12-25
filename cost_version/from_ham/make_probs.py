# This script generates learning probabilities for field and not field

import pandas as pd
import math
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np

def gen_probs(row, kfrac, field):
    num = math.exp(row['alp'] + row[' bet'] * kfrac + field)
    return num / (1 + num)

def ratio(alp,bet,lt):
    """creates prob ratio"""
    num0 = np.exp(alp + lt)
    num5 = np.exp(alp + bet * 0.05 + lt)
    rat = np.log(num5 / (1 + num5)) - np.log(num0 / (1 + num0))
    return rat

def gen_probrat(row,lt):
    """ creates prob improvement for average latent type """
    #lt = 0.5 * row[' lat_prob1'] + 0.05 * row[' lat_prob2']
    num0 = math.exp(row['alp'] + lt)
    num5 = math.exp(row['alp'] + row[' bet'] * 0.05 + lt)
    rat = math.log(num5 / (1 + num5)) - math.log(num0 / (1 + num0))
    return rat

if __name__ == '__main__':
    """git er done"""

    #READ IN DATA
    dat = pd.read_csv('out.csv')
    dat = dat.ix[np.random.random_integers(0, len(dat), 1000)]
    
    # lf0   = dat.apply(lambda row: gen_probs(row, 0.0, -5), axis=1)
    # lf10  = dat.apply(lambda row: gen_probs(row, 0.05, -5), axis=1)
    # mf0      = dat.apply(lambda row: gen_probs(row, 0.0, -3.5), axis=1)
    # mf10     = dat.apply(lambda row: gen_probs(row, 0.05, -3.5), axis=1)
    # hf0      = dat.apply(lambda row: gen_probs(row, 0.0, -1), axis=1)
    # hf10     = dat.apply(lambda row: gen_probs(row, 0.05, -1), axis=1)
    # learn_probs = pd.DataFrame({ 'low lat 0%': lf0, 'mid lat 0%': mf0, 'high lat 0%': hf0, 'low lat 5%': lf10, 'mid lat 5%': mf10, 'high lat 5%': hf10})
    # learn_probs = learn_probs[['low lat 0%', 'mid lat 0%', 'high lat 0%', 'low lat 5%', 'mid lat 5%', 'high lat 5%']]
    # 
    # print learn_probs
    
    # fig, axes = plt.subplots(nrows=2, ncols=3)
    # learn_probs['low lat 0%'].hist(bins=25, ax=axes[0,0], figsize=(17,8)); axes[0,0].set_title('low lat 0%'); axes[0,0].set_xlim([0,1])
    # learn_probs['mid lat 0%'].hist(bins=25, ax=axes[0,1], figsize=(17,8)); axes[0,1].set_title('mid lat 0%'); axes[0,1].set_xlim([0,1])
    # learn_probs['high lat 0%'].hist(bins=25, ax=axes[0,2], figsize=(17,8)); axes[0,2].set_title('high lat 0%'); axes[0,2].set_xlim([0,1])
    # learn_probs['low lat 5%'].hist(bins=25, ax=axes[1,0], figsize=(17,8)); axes[1,0].set_title('low lat 5%'); axes[1,0].set_xlim([0,1])
    # learn_probs['mid lat 5%'].hist(bins=25, ax=axes[1,1], figsize=(17,8)); axes[1,1].set_title('mid lat 5%'); axes[1,1].set_xlim([0,1])
    # learn_probs['high lat 5%'].hist(bins=25, ax=axes[1,2], figsize=(17,8)); axes[1,2].set_title('high lat 5%'); axes[1,2].set_xlim([0,1])
    # fig.tight_layout()
    # plt.savefig('learn_probs.png', bbox_inches=0)
    
    # GET MEDIAN TYPE
    ff = pd.read_pickle('first_ff.pickle')
        
    fig = plt.figure() 
    grid = np.linspace(-5,5,20)
    y = []
    for k in range(20):
        prob_inc = dat.apply(lambda row: gen_probrat(row,grid[k]), axis=1).describe()['50%']
        y.append(prob_inc)
             
    ax1 = fig.add_subplot(1,1,1)
    plt.plot(grid,y)
    plt.xlabel('Latent type')
    plt.ylabel('Expected log difference in annual learning prob.')
    ax2 = ax1.twinx()

    typ = dat[' lat_prob1'].describe()['mean'] * ff['dep_qual']\
            + dat[' lat_prob2'].describe()['mean'] * ff['dmean']

    typ.hist(bins=25,alpha=0.2,ax=ax2,normed=True)
    plt.axis('off')
    
    plt.savefig('learn_probs.png', bbox_inches=0)
    # plot_dat = pd.DataFrame([prob_inc,typtype]).T
    # kde = stats.kde.gaussian_kde(plot_dat.T)

    # # Regular grid to evaluate kde upon
    # x_flat = np.linspace(plot_dat[0].min(),plot_dat[0].max(),num=70)
    # y_flat = np.linspace(plot_dat[1].min(),plot_dat[1].max(),num=70)
    # x,y = np.meshgrid(x_flat,y_flat)
    # grid_coords = np.append(x.reshape(-1,1),y.reshape(-1,1),axis=1)

    # z = kde(grid_coords.T)
    # z = z.reshape(70,70)

    # plt.contour(x, y, z, colors ='k')
    
    plt.show()


