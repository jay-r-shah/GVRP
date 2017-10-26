# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 16:01:55 2017

@author: Jay
"""

import numpy as np
import matplotlib.pyplot as plt

depot = np.array([[50,50]])
xy = np.random.randint(1,100,size=(49,2))
xy = np.concatenate((depot,xy),0)
#plt.plot(depot[0],depot[1],"o")
#plt.plot([x for x in xy[:,0]],[y for y in xy[:,1]],"*")

for i in range(len(xy)):
    plt.plot(xy[i,0],xy[i,1],"*b")
    plt.text(xy[i,0]+1,xy[i,1]-1,str(i))

def print2file(xy):
    strxy = str(xy)
    strxy = strxy.replace("[ ","[")
    strxy = strxy.replace(" ",",")
    strxy = strxy.replace(",,",",")
    strxy = strxy.replace("\n","")
    text_file = open("GVRPdata.dat", "w")
    text_file.write(strxy)
    text_file.close()