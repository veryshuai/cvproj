# This script calls the main estimation loop for discrete version of my model

import pandas as pd


def main():

    #INITIAL PARAMETERS (TO BE MOVED)
    alp = tree()
    gam = tree()
    for qual in range(3):
        for field in range(2):
            for lat in range(2):
                alp[qual][field][lat] = 0.1
                gam[qual][field][lat] = 0.1
    


