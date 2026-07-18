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

from src.utils.base_paths import get_reference_data_path
from src.utils.auto_enum import AutoEnum, auto, alias

class CropType(AutoEnum):
    wheat = alias('durum', 'durum wheat')
    barley = auto()
    canola = auto()
    lupins = auto()
    peas = auto()
    vetch = auto()
    oat = alias('oats')
    triticale = auto()
    pasture = alias('clover', 'chicory', 'perennial ryegrass', 'subclover', 'brassica', 'tillage radish', 'balansa clover')
    lentil = auto()
    chickpea = auto()
    fababean = alias('faba beans', 'faba', 'fb')
    fieldpea = alias('field peas')
    millet = auto()
    greenmanure = alias('warm cover mix', 'cover crop')
    fallow = auto()

def checkPlotState(plot_id, plotActivityType, year, month, day, crop1=None, crop2=None, crop3=None, current_state=None):

    #Conduct checks
    if not (plotActivityType == 'SOWING' or plotActivityType == 'TERMINATION'):
        raise NameError("plotActivityType must be either 'SOWING' or 'TERMINATION'.")

    if(plotActivityType=='TERMINATION' and crop1 == None):
        raise ValueError("Check plot " + plot_id + ". At a minimum, the 'crop1' argument must be non-empty if you are seeking to enter a crop termination data observation")

    #Determine the plot's state that applies to THIS event. Two modes:
    #  * current_state supplied (used by the chronological batch validator, validate_crop_state_activities):
    #    the caller passes the plot's running state as a dict {'STATE','CROP1','CROP2','CROP3'} so state
    #    changes made earlier in the same run are visible without re-reading the .csv. This is what makes
    #    loading multiple seasons / both activities in one run work.
    #  * current_state omitted (legacy/standalone use): read plotStateData.csv and take the most recent
    #    state recorded ON OR BEFORE the event date (as-of-date) rather than the global-latest row, so a
    #    single check does not depend on the order in which later events were loaded.
    if current_state is not None:
        plot_state_STATE = current_state.get('STATE')
        plot_state_CROP1 = current_state.get('CROP1')
        plot_state_CROP2 = current_state.get('CROP2')
        plot_state_CROP3 = current_state.get('CROP3')
    else:
        #read in state data
        try:
            plot_state_data = pd.read_csv(get_reference_data_path('PlotStateData.csv'))
        except FileNotFoundError as e:
            raise e

        #subset df by plotID
        plot_data = plot_state_data.loc[plot_state_data['PLOT_ID'] == plot_id]
        plot_data = plot_data.replace({np.nan: None})
        #if no data return an error message indicating that it is necessary to instatiate all plots with a starting state
        if plot_data.empty:
            raise ValueError("There is no entry in the plot state data for" + plot_id + ". Please ensure a starting state is initiated for ALL plots prior to data entry")

        #parse dates properly (string sorting mis-orders dates like '1/01/2023' vs '10/05/2024')
        plot_data = plot_data.copy()
        plot_data['DATE'] = pd.to_datetime(plot_data['DATE'], format='mixed', dayfirst=True)
        event_date = datetime.datetime(year, month, day)

        #use the most recent state recorded on or before the event date (state 'as of' this event)
        prior_states = plot_data.loc[plot_data['DATE'] <= event_date].sort_values(by='DATE')
        if prior_states.empty:
            raise ValueError("There is no plot state recorded on or before " + str(event_date.date()) + " for " + plot_id + ". Ensure a starting state (dated on or before the first event) exists for ALL plots prior to data entry")

        latest_state = prior_states.tail(1)
        plot_state_STATE = latest_state['STATE'].item()
        plot_state_CROP1 = latest_state['CROP1'].item()
        plot_state_CROP2 = latest_state['CROP2'].item()
        plot_state_CROP3 = latest_state['CROP3'].item()

    #convert strings to lower with no white space
    if not plot_state_CROP1 == None:
        plot_state_CROP1 = CropType(plot_state_CROP1.lower().strip())
    if not plot_state_CROP2 == None:
        plot_state_CROP2 = CropType(plot_state_CROP2.lower().strip())
    if not plot_state_CROP3 == None:
        plot_state_CROP3 = CropType(plot_state_CROP3.lower().strip())

    if not crop1 == None:
        crop1 = CropType(crop1.lower().strip())
    if not crop2 == None:
        crop2 = CropType(crop2.lower().strip())
    if not crop3 == None:
        crop3 = CropType(crop3.lower().strip())

    #if plotActivityType = 'TERMINATION' and STATE = 'CROP' fail and pass error message
    if (plotActivityType == 'TERMINATION' and plot_state_STATE == 'FALLOW'):
        raise ValueError("Plot " + plot_id + " is already in a fallow state. You cannot terminate a fallow state")

    #Else, check the opposite condition:
    elif(plotActivityType == 'SOWING' and plot_state_STATE == 'CROP'):
        raise ValueError("Plot " +  plot_id + " is already sown to a crop and no termination event has been recorded yet. Please enter a termination record first.")

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

    return newrow
