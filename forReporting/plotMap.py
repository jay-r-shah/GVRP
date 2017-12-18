# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 00:06:49 2017

@author: Jay
"""

'''
.py file to create customer/cluster map and vehicle routes for the generalized vehicle routing
problem (GVRP)
'''


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
import math

DPI = 300

def parseData(filename):
    data = [];
    with open(filename) as f:
        for line in f:
            data.append(eval(line))
    return data;
    
def parseSolution(filename):
    data = [];
    with open(filename) as f:
        for line in f:
            points = line.split(" ")
            if points[0] == "Sol":
                title = line[4:]
            elif points[0] == "Cost":
                cost = line[5:]
            elif points[0] == "DataFile":
                dataFileName = line[9:]
            elif points[0] == "Gap":
                gap = float(points[1])
            else:
                data.append([int(points[0]), int(points[1])])
                
    return data,title,cost,gap,dataFileName

def plotCoords(solFileName):
    solData,title,cost,gap,dataFileName = parseSolution(solFileName)
    data = parseData("../data/"+dataFileName+".dat")
    xy = np.array(data[0])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i in range(len(xy)):
        ax.plot(xy[i,0],xy[i,1],"*b")
        # ax.text(xy[i,0]+1,xy[i,1]-1,str(i)) # Uncomment if you want customer labels
    clusters = np.array(data[1])
    depot = [xy[clusters[0],0],xy[clusters[0],1]]
    ax.add_patch(mpatches.Rectangle((depot[0] - 3, depot[1] -3), 6, 6, fill=False))
    ax.set_xlim(left=0, right=80)
    ax.set_ylim(bottom=0, top = 80)
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

            x_diff_squared = [element**2 for element in x_diff]
            slope = sum(x * y for x,y in zip(x_diff, y_diff)) / sum(x_diff_squared)
            angle = math.atan(slope)
            xDist = 2*(x2 - x1)/math.cos(angle)
            yDist = 2*(y2 - y1)*math.cos(angle)
            if yDist == 0:
                yDist = 0.5*(xDist+5)
            ellipse1 = mpatches.Ellipse((x0,y0), xDist, yDist,np.rad2deg(angle),fill = False)
            ax.add_artist(ellipse1)
    
    resFileName = solFileName[solFileName.rfind("/")+1:]
    solData = np.array(solData)
    # ax.set_title(title + "Cost = " + cost + " Gap = " + str(round(gap*100,2)) + "%\n")
    for arc in solData:
        node1 = arc[0]
        node2 = arc[1]
        x1 = xy[node1][0] ; y1 = xy[node1][1]
        x2 = xy[node2][0] ; y2 = xy[node2][1]
        if node1 == 0 or node2 == 0: # Dotted line if going to or coming from depot
            ax.plot([x1,x2],[y1,y2],'--b')
        else:
            ax.plot([x1,x2],[y1,y2],'b')

    plt.tight_layout()
    fig.savefig("images/"+resFileName[:-4]+'_map'+'.png', dpi=DPI, bbox_inches='tight')

#####################################################################################################################
def readArgs():
    """
    Reading the command line arguments and performing basic checks
    :return: the list of arguments
    """
    args = sys.argv
    if len(args) != 2:
        print(len(args))
        print("ERROR - Wrong number of arguments! \n")
        print("Usage:  plotMap.py <path to problemData>")
        exit(5)
    return args

if __name__ == "__main__":
    args = readArgs()
    if len(args)==2:
        plotCoords(args[1])
    else:
        print("Usage:  plotMap.py <path to solutionData>")
        exit(5)