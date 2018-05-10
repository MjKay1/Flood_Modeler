# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 10:36:55 2018

@author: Matt
"""


def makescalar(diff, group_total, flow_scalar):
    """
    creates flow_scalar list 
    
    sums the drop in elevation in cells that are downslope. then divides total from individual drop to make a 
    precentage.
    
    
    arguments-
    
    diff - float
    flow_scalar - float
    group_total - float
    
    
    returns -
    
    flow_scalar - float
    """
    #calcule total downhill slopes, to compare to slope in each direction to allocate percentage of water flow
    if diff > 0:                                #if downslope
        group_total += diff                     #add difference in height to total
        flow_scalar.append(diff/group_total)    #append to flow_scalar the relative amount of flow to that cell 
    else:
        flow_scalar.append(0)                   #else append 0 flow to cell
        

def checkmax(diff, rain_area, max_output):
    """
    checks stored rain against max flow 
    
    if the stored rain is over the max_output it limits flow to the max_output
    
    
    arguments-
    
    diff - float
    rain_area - float
    max_output - float
    
    
    returns -
    
    checkmax.flow - float
    """
    if diff > 0:                                #if downslope
        if rain_area < max_output:              #if lower than max_output
            checkmax.flow = rain_area           #flow equal to whole store
        else:
            checkmax.flow = max_output          #else flow equal to max_output
 
          
def addrain(rain_area, rainfall):
    """
    adds rainfall
    
    increases rain_area in each cell by value specified by rainfall
    
    
    arguments-
    
    rain_area - float
    rainfall- float
    
    
    returns -
    
    rain_area - float
    """
    for i in range (len(rain_area)):            #for each data point
        for j in range (len(rain_area)):    
            rain_area[i][j] += rainfall         #add rainfall to total water store (rain_area)


def clear(diff, flow_scalar, group_total):
    """
    clears list and resets values
    
    resets lists and values in preperation for the next cell to be processed
    
    
    arguments-
    
    diff - float
    flow_scalar - float
    group_total - float
    
    
    returns -
    
    group_total - float
    """
    diff.clear()
    flow_scalar.clear()
    group_total = 0
    return group_total
