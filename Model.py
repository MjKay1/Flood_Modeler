# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 11:54:04 2018

@author: Matt


Basic flood modeler- models where rainwater flows to in an environment, and shows how water will 'back-up'
when rainfall exceeds output flow.


the DEM used in this model is taken from Edina Digimap and is OS tile NN50 (Trossachs area, Scotland).
(This could be any DEM or list of values and needs to be saved as "input_elevations.txt").
the elevation data is used to calculate the change in height between neighbouring cells to determine flow direction,
in the case of multiple 'downslope' neighbours, a weighting is given to each based on angle of slope
(largest change in elevation).

A second nessed list is created, containing a set amount of rainfall, and this rainfall amount is passed downslope
to neighbours based on the above calculation. This is done from the highest point in the area downwards to negate
'wave affect' of scanning left to right, top down. in the case of a flat area, the total of both cells stored rain
is shared equally between neighbour and itself.

Running the code will bring up a GUI displaying the DEM, where the model can be run and an animation showing the
flooding conditions day by day will play, stopping when the days_rain variable is reached. The final water levels
are then stored ("waterlevels.txt").


arguments-

environment input (input_elevations.txt) - float
rainfall - float
days_rain - int
max_output - float
matplotlib.pyplot.figure(figsize) - int


returns-

figure showing environment
animation showing flood levels day by day
final water level output (waterlevels.txt) - float
"""

import cellframework
import csv
import matplotlib.pyplot
import matplotlib.animation
import tkinter
import matplotlib.backends.backend_tkagg


#load in data (raster of elevations)
f = open('input_elevations.txt', newline='')            #add raster height data to 'input_elevations.txt' file (comma delimited), this file is opened and data appended. 
environment = []                                        #create environment list
reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
for row in reader:
    rowlist = []                                        #create rowlist list
    for value in row:
        rowlist.append(value)                           #append values in each row to rowlist list
    environment.append(rowlist)                         #append all rowlists to environment list
f.close()


area = []


#create window for animation
fig = matplotlib.pyplot.figure(figsize=(10,10))


#set variables
rainfall = 10
days_rain = 10


#show environment data before program runs, this is useful for both comparing to
#water accumulation and to check environment has loaded correctly
matplotlib.pyplot.imshow(environment)       


#create array matching environment to contain rainfall, and append 'rainfall' variable to each cell
rain_area = []
for i in range (len(environment)):
    rain_row = []
    for j in range (len(environment[i])):
        rain_row.append(rainfall)
    rain_area.append(rain_row)

        
carry_on = True


#set what happens each repeat of frame in animation
def update(frame_number):
    """
    until stopping condition in met it adds more rainfall to whole area, and repeats process of moving water 
    downslope.
    
    
    stopping condition set to be 'days_rain', if frame number value is less than value specified by 'days_rain'
    it will add another frame to the animation and repeat the process below. 
    
    On repeat the differences of elevations between neighbouring cells area calculated, starting with the highest
    value cell (the maximum elevation) and then incrementaly down to lower cells. For neighbouring cells that are
    downslope, a 'flow_scalar' is created to give a weighted precentage to each cell based on size of height
    difference. The cell will then pass a percentage of it's 'rain_area' value (up to the value specified by 
    'max_output') onto each neighbouring downslope cell based on the 'flow_scalar'. if there are no downslope 
    areas, any equal height neighbour will sum its 'rain_area' value with the cell and this total will be shared
    equally between them. 
    
    the stopping condition criteria is then checked again, and the frame for the animation is produced.
    
    
    arguments-
    
    environment - float
    max_output - float
    rain_area - float
    rainfall - float
    
    
    returns-
    
    frame in animation
    waterlevels.txt - float
    prints stopping statement - text
    """
    
    fig.clear()
    global carry_on


    #create lists and variables used in program
    diff = []
    max_output = 10    #set the maximum amount of rain that can be passed out of each cell
    group_total = 0
    flow_scalar = []

    
    #find the highest point in the area, as the values will be processed in height order
    max_row = list(map(max,environment[1:-1]))
    max_elevation = max(max_row[1:-1])
    
    
    #run process on each cell (check for high point, compare height of neightbours and pass water to lower cells)
    for i in range (len(environment[1:-1])):                            #only run process on cells within a 1 cell of edge to ensure all have 8 neighbours
        for j in range (len(environment[i][1:-1])):
            if environment[i][j] >= max_elevation:                      #check each cell for if it is the highest point, and run if it is
                diff.append(environment[i][j]-environment[i-1][j-1])    #calculate the differences in altitude with 8 surrounding cells
                diff.append(environment[i][j]-environment[i-1][j])
                diff.append(environment[i][j]-environment[i-1][j+1])
                diff.append(environment[i][j]-environment[i][j-1])
                diff.append(environment[i][j]-environment[i][j+1])
                diff.append(environment[i][j]-environment[i+1][j-1])
                diff.append(environment[i][j]-environment[i+1][j])
                diff.append(environment[i][j]-environment[i+1][j+1])
                
                
                for k in range (len (diff)):
                    #calcule total downhill slopes, to compare to slope in each direction to allocate percentage of water flow
                    cellframework.makescalar(diff[k], group_total, flow_scalar)
                    #check if cell has water stores above the max_output and limit to max_output if so.
                    cellframework.checkmax(diff[k],rain_area[i][j], max_output)
                
                
                #allocate a percetage of water output to each downhill direction based on highest angle of slope.
                for k in range (len(diff)):
                    if diff[k] > 0:                                     #if downslope
                        x = (k%3)-1                                     #set the relative x co-ordinate based on 'k' number in diff list 
                        y = (int((k - x)/3))-1                          #set the relative y co-ordinate based on 'k' number in diff list
                        if rain_area[i][j] + environment[i][j] > rain_area[i+x][j+y] + environment[i+x][j+y]:   #prevent "water piles" by making sure flood water stays level 
                            rain_area[i+x][j+y] =+ (cellframework.checkmax.flow*flow_scalar[k])    #allocate a percetage of water output to each downhill direction based on angle of slope (flow_scalar).
                                 
                    
                #level ground rule (prevent water for building up at the edge of a level feature)
                for k in range (len(diff)):
                    if all (values <= 0 for values in diff):            #check no downslope cell to flow to
                        if diff[k] == 0:                                #if neightbouring cell is level
                            x = (k%3)-1                                 #set the relative x co-ordinate based on 'k' number in diff list
                            y = (int((k - x)/3))-1                      #set the relative x co-ordinate based on 'k' number in diff list
                            rain_share = (rain_area[i][j] + (rain_area[i+x][j+y]))/2    #share total of rain_area between cell and neighbouring level cell
                            rain_area[i][j] = rain_share
                            rain_area[i+x][j+y] = rain_share
                
                
                #clear values and lists in preperation for next cell
                cellframework.clear(diff, flow_scalar, group_total)
                
                
            #once all values at that elevation are processed, lower elevation by 0.1 and check for cells at new lower elevation.    
            
            max_elevation =- 0.1

     
    #add rainfall for next day        
    cellframework.addrain(rain_area,rainfall)
    
        
    #plot rain_area for each day    
    matplotlib.pyplot.ylim(len(environment))        #set ylim to amount of lists in environment list
    matplotlib.pyplot.xlim(len(environment[i]))     #set xlim to number of values within environment list lists
    matplotlib.pyplot.gca().invert_xaxis()
    matplotlib.pyplot.imshow(rain_area)


    #export final rain_area to 'waterlevels.txt' 
    f2 = open('waterlevels.txt', 'w', newline='') 
    writer = csv.writer(f2, delimiter=' ')
    for row in rain_area:		
    	writer.writerow(row)
    f2.close()


#check for repeat
def gen_function(b = [0]):
    """
    requires no setup
    """
    a = 0
    global carry_on
    while (a < days_rain) & (carry_on):     #set stopping parameter to 'days_rain' variable
        yield a			
        a = a + 1                           #add 1 to 'a' value if carry on 
    else:
        print("Flooding Conditions after",rainfall,"unit(s) of Daily Rainfall over",days_rain," Days")     #print stopping statement
     

#set animation to run
def run():
    """
    requires no setup
    """
    animation = matplotlib.animation.FuncAnimation(fig, update, frames=gen_function, repeat=False)
    canvas.show()


#build GUI
root = tkinter.Tk() 
root.wm_title("Model")
canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(fig, master=root)
canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
menu_bar = tkinter.Menu(root)
root.config(menu=menu_bar)
model_menu = tkinter.Menu(menu_bar)
menu_bar.add_cascade(label="Model", menu=model_menu)
model_menu.add_command(label="Run model", command=run) 


tkinter.mainloop()