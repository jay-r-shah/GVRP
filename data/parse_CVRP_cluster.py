# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 19:16:21 2017

@author: Jay
"""

from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math

N = 49

def parseData(filename):
    nodes = [];
    demands = [];
    typeOfData = "data"
    with open(filename) as f:
        for line in f:
            words = line.split(" ")
            try:
                words.remove('')
            except:
                pass
            try:
                words.remove('\t')
            except:
                pass
            try:
                words.remove('\n')
            except:
                pass
            if typeOfData == "data":
                if words[0] == "NAME":
                    name = words[-1].strip()
                if words[0] == "NODE_COORD_SECTION" or words[0] == "NODE_COORD_SECTION\n":
                    typeOfData = "nodes"
            elif typeOfData == "nodes":
                if words[0] == "DEMAND_SECTION" or words[0] == "DEMAND_SECTION\n":
                    typeOfData = "demands"
                else:
                    nodes.append([float(words[1]),float(words[2])])
            elif typeOfData == "demands":
                if words[0] == "DEPOT_SECTION" or words[0] == "DEPOT_SECTION\n":
                    typeOfData = "depot"
                else:
                    demands.append(float(words[1]))
            else:
                pass
    return name,nodes,demands

def createData(CVRPdatafile):
    name,nodes,demands = parseData(CVRPdatafile)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i in range(len(nodes)):
        ax.text(nodes[i][0]+1,nodes[i][1]-1,str(i))
        ax.plot(nodes[i][0],nodes[i][1],"*b")
    X = np.array(nodes[1:])
    kmeans = KMeans(n_clusters=N, random_state=0).fit(X)
    clusters = []
    
    for nCluster in range(N):
        thisCluster = [];
        for i in range(len(kmeans.labels_)):
            if nCluster == kmeans.labels_[i]:
                thisCluster.append(i+1)
        clusters.append(thisCluster)
    
    clusters.insert(0,[0])
    
    clusterDemands=[];
    
    for cluster in clusters:
        totaldemand = 0;
        for customer in cluster:
            totaldemand += demands[customer]
        clusterDemands.append(totaldemand)
        
        
    strxy = str(nodes)
    strcl = str(clusters)
    strdem = str(clusterDemands)
    
    strxy = strxy.replace("[ ","[")
    strxy = strxy.replace(" ",",")
    strxy = strxy.replace(",,",",")
    strxy = strxy.replace("\n","")
    
    strcl = strcl.replace("[ ","[")
    strcl = strcl.replace(" ",",")
    strcl = strcl.replace(",,",",")
    strcl = strcl.replace("\n","")
    
    strdem = strdem.replace("[ ","[")
    strdem = strdem.replace(" ",",")
    strdem = strdem.replace(",,",",")
    strdem = strdem.replace("\n","")
    
    text_file = open(name + "-c" + str(N) + ".dat", "w")
    text_file.write(strxy + "\n")
    text_file.write(strcl)
    text_file.write("\n")
    text_file.write(strdem)
    
    text_file.close()
    xy = np.array(nodes)
    
    for i in range(len(xy)):
        ax.plot(xy[i,0],xy[i,1],"*b")
        ax.text(xy[i,0]+1,xy[i,1]-1,str(i))
    depot = [xy[clusters[0],0],xy[clusters[0],1]]
    ax.add_patch(mpatches.Rectangle((depot[0] - 3, depot[1] -3), 6, 6, fill=False))
    
    for cluster in clusters[1:]:
        if len(cluster) == 1:
            circle1 = plt.Circle((xy[cluster[0],0],xy[cluster[0],1]), 3, fill = False)
            ax.add_artist(circle1)
        if len(cluster) == 2:
            centerX = (xy[cluster[0],0] + xy[cluster[1],0])/2
            centerY = (xy[cluster[0],1] + xy[cluster[1],1])/2
            xDist = np.sqrt((xy[cluster[0],0] - xy[cluster[1],0])**2 + (xy[cluster[0],1] - xy[cluster[1],1])**2)
            yDist = 0.5*(xDist+5)
            angle = math.atan((xy[cluster[0],1] - xy[cluster[1],1])/(xy[cluster[0],0] - xy[cluster[1],0]))
            ellipse1 = mpatches.Ellipse((centerX,centerY), xDist+5, yDist,np.rad2deg(angle),fill = False)
            ax.add_artist(ellipse1)
        if len(cluster) > 2:
            xData = [];
            yData = [];
            for point in cluster:
                xData.append(xy[point,0])
                yData.append(xy[point,1])
            x1 = min(xData); x2 = max(xData);
            y1 = min(yData); y2 = max(yData);
            x0 = (x1+x2)/2; y0 = (y1+y2)/2;
            avg_x = sum(element for element in xData)/len(xData)
            avg_y = sum(element for element in yData)/len(yData)
            
            x_diff = [element - avg_x for element in xData]
            y_diff = [element - avg_y for element in yData]
    #            stddev = np.std(data2,axis=0)
    
            x_diff_squared = [element**2 for element in x_diff]
            slope = sum(x * y for x,y in zip(x_diff, y_diff)) / sum(x_diff_squared)
    #            slope = (y2-y1)/(x2-x1)
            angle = math.atan(slope)
            xDist = 2*(x2 - x1)/math.cos(angle)
            yDist = 2*(y2 - y1)*math.cos(angle)
            if yDist == 0:
                yDist = 0.5*(xDist+5)
            ellipse1 = mpatches.Ellipse((x0,y0), xDist, yDist,np.rad2deg(angle),fill = False)
            ax.add_artist(ellipse1)

createData('P-n50-k10.dat')