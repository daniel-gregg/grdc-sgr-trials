import sys
from pyprojroot.here import here

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

import pandas as pd
import numpy as np
import datetime
import csv
#plotActivityType must be either 'SOWING' or 'TERMINATION' and comes from the pydantic 
#validator path (defined post validation)
#crop1 is required if plotActivityType = 'TERMINATION'
#crop2 and crop3 are optional for plotActivityType 'TERMINATION'
#all cropX arguments are ignored for plotActivityType 'SOWING'

def checkPlotState(plot_id, plotActivityType, year, month, day, crop1=None, crop2=None, crop3=None):
    print(plotActivityType)
    #Conduct checks
    if not (plotActivityType == 'SOWING' or plotActivityType == 'TERMINATION'):
        raise NameError("plotActivityType must be either 'SOWING' or 'TERMINATION'.")
    
    if(plotActivityType=='TERMINATION' and crop1 == None):
        raise ValueError("Check plot " + plot_id + ". At a minimum, the 'crop1' argument must be non-empty if you are seeking to enter a crop termination data observation")
    
    #read in state data
    try:
        plot_state_data = pd.read_csv(here('src/sgr_data/data/PlotStateData.csv'))
    except FileNotFoundError as e:
        raise e

    #subset df by plotID
    plot_data = plot_state_data.loc[plot_state_data['PLOT_ID'] == plot_id]
    plot_data = plot_data.replace({np.nan: None})
    #if no data return an error message indicating that it is necessary to instatiate all plots with a starting state
    if plot_data.empty:
        raise ValueError("There is no entry in the plot state data for" + plot_id + ". Please ensure a starting state is initiated for ALL plots prior to data entry")
    
    #order the data by date and get most recent data
    plot_data_sorted = plot_data.sort_values(by="DATE")
    plot_state_STATE = plot_data_sorted.tail(1)['STATE'].item() #gets the last entry after being sorted (ascending is default)
    plot_state_CROP1 = plot_data_sorted.tail(1)['CROP1'].item() #gets the last entry after being sorted (ascending is default)
    plot_state_CROP2 = plot_data_sorted.tail(1)['CROP2'].item() #gets the last entry after being sorted (ascending is default)
    plot_state_CROP3 = plot_data_sorted.tail(1)['CROP3'].item() #gets the last entry after being sorted (ascending is default)

    #if plotActivityType = 'TERMINATION' and STATE = 'CROP' fail and pass error message
    if (plotActivityType == 'TERMINATION' and plot_state_STATE == 'FALLOW'):
        raise ValueError("Plot " + plot_id + "is already in a fallow state. You cannot terminate a fallow state")
    
    #Else, check the opposite condition:
    elif(plotActivityType == 'SOWING' and plot_state_STATE == 'CROP'):
        raise ValueError("Plot " +  plot_id + "is already sown to a crop and no termination event has been recorded yet. Please enter a termination record first.")

    #Finally, check that the stated harvested crops are the same as those that were last planted
    elif(plotActivityType == 'TERMINATION'):
        plot_states_set = set([plot_state_CROP1,plot_state_CROP2,plot_state_CROP3])
        if crop1 not in plot_states_set:
            raise ValueError("Check plot " + plot_id + ". Terminated crops must match planted crops\n Crop" + crop1 + "not in planted set")   
        if crop2 is not None:
            if crop2 not in plot_states_set:
                raise ValueError("Check plot " + plot_id + ". Terminated crops must match planted crops\n Crop" + crop2 + "not in planted set")   
        if crop3 is not None:
            if crop3 not in plot_states_set:
                raise ValueError("Check plot " + plot_id + ". Terminated crops must match planted crops\n Crop" + crop3 + "not in planted set")       
        
    ## At this stage, the sowing/termination data are valid - update plot-state data table
    if plotActivityType=="SOWING":
        state = "CROP"
    else:
        state = "FALLOW"

    newrow = pd.DataFrame({
        'PLOT_ID' : [plot_id],
        'DATE' : [datetime.datetime(year,month,day)], 
        'STATE' : [state],
        'CROP1' : [crop1],
        'CROP2' : [crop2],
        'CROP3': [crop3]
    })

    #write new line to plotStateData.csv
    newrow.to_csv(here('src/sgr_data/data/PlotStateData.csv'), mode='a', index=False, header=False)

    return newrow
