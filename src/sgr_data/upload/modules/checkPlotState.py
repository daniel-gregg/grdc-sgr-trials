import sys
from pyprojroot.here import here

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

import pandas as pd

#plotActivityType must be either 'SOWING' or 'TERMINATION' and comes from the pydantic 
#validator path (defined post validation)
#crop1 is required if plotActivityType = 'TERMINATION'
#crop2 and crop3 are optional for plotActivityType 'TERMINATION'
#all cropX arguments are ignored for plotActivityType 'SOWING'

def checkPlotState(plot_id, plotActivityType, crop1=None, crop2=None, crop3=None):
    
    #Conduct checks
    if (plotActivityType!='SOWING' or type!='TERMINATION'):
        NameError("plotActivityType must be either 'SOWING' or 'TERMINATION'.")
    
    if(plotActivityType=='TERMINATION' and crop1 == None):
        ValueError("At a minimum, the 'crop1' argument must be non-empty if you are seeking to enter a crop termination data observation")
    
    #read in state data
    try:
        plot_state_data = pd.read_csv(here('src/sgr_data/data/PlotStateData.csv'))
    except:
        #If no actual data available, read in the test data
        try:
            plot_state_data = pd.read_csv(here('src/sgr_data/data/test_data/plotStateData.csv'))
            print("Note that you have not specified a plotStateData dataset so the TEST data is being used")
        
        except: 
            return "no plot state data ('plotStateData.csv') exists in expected directory (.../sgr_data/data)"

    #subset df by plotID
    plot_data = plot_state_data.loc[plot_state_data['PLOT_ID'] == plot_id]

    #if no data return an error message indicating that it is necessary to instatiate all plots with a starting state
    if plot_data.empty:
        ValueError("There is no entry in the plot state data for" + plot_id + ". Please ensure a starting state is initiated for ALL plots prior to data entry")
    
    #check if plot state is 'CROP' or 'FALLOW'
    else:
    
        #order the data by date and get most recent data
        plot_data_sorted = plot_data.sort_values(by="DATE")
        plot_state_STATE = plot_data_sorted.tail(1)['STATE'] #gets the last entry after being sorted (ascending is default)
        plot_state_CROP1 = plot_data_sorted.tail(1)['CROP1'] #gets the last entry after being sorted (ascending is default)
        plot_state_CROP2 = plot_data_sorted.tail(1)['CROP2'] #gets the last entry after being sorted (ascending is default)
        plot_state_CROP3 = plot_data_sorted.tail(1)['CROP3'] #gets the last entry after being sorted (ascending is default)

        #if plotActivityType = 'TERMINATION' and STATE = 'CROP' fail and pass error message
        if (plotActivityType == 'TERMINATION' & plot_state_STATE == 'FALLOW'):
            ValueError("Plot" + plot_id + "is already in a fallow state. You cannot terminate a fallow state")
        
        #Else, check the opposite condition:
        elif(plotActivityType == 'SOWING' & plot_state_STATE == 'CROP'):
            ValueError("Plot" +  plot_id + "is already sowed to a crop and no termination event has been recorded yet. Please enter a termination record first.")

        #Finally, check that the stated harvested crops are the same as those that were last planted
        elif(plotActivityType == 'TERMINATION'):
            if(set([plot_state_CROP1,plot_state_CROP2,plot_state_CROP3]) not in set([crop1, crop2, crop3])):      
                ValueError("Terminated crops must match planted crops")   
            else: 
                return plot_id
