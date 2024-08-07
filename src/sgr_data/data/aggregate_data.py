## This function allows for aggregation of activity and plot data
# aggregation is applied using the plot_id string that encapsulates key data about trial/site relationships
# aggregation can also undertaken across time

# Plot id example
# APPILA_S3_P1234_R1
# APILLA = site name
# S3 = system (overall program treatment groups across sites)
# P1234 = phase --> a plot may be in the same system but have a different phase (sequence of the same crops differs across time)
# R1 = replicate number

# This ID approach provides for a range of strategies to aggregate up, for example to get:
# get all basic replicates on a site - remove the last three characters of the string and match
# get all basic replicates across all sites - as above, plus remove the site string and match
# get all system replicates on a site - remove everything after "S3" and match
# get all site plots - retain only the site string and match

# base imports
from pyprojroot.here import here
import sys
import os
from copy import deepcopy
from pydantic import ValidationError

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

import pandas as pd

####### utility functions (export to utilities once working)

# Get all activity and state data by plot ID
def getDataByPlot(plotID):
    ### get state-plot data
    state_plot = pd.read_csv(os.path.join('src','sgr_data','data','plotStateData.csv'))
    state_plot_site = state_plot.loc[state_plot['PLOT_ID']==plotID,]

    ### get string elements
    str_args = plotID.split("_")

    site = str_args[0]
    system = str_args[1]
    phase_sequence = str_args[2]
    rep_id = str_args[3]

    ### get site directory for validated data
    site_path = os.path.join('src','sgr_data','data','validated_data','site')
    activities_list = os.listdir(site_path) # this gets the activity folders in the validated data for the target site

    activities_data_dict = {activity: [] for activity in activities_list}

    for activity in activities_list:
        pd.read_pickle
    data_dict = {
        'state' : state_plot_site,
        'fertiliser' : fertiliser,
        'fungicide' : fungicide,
        'herbicide' : herbicide,
        'pesticide' : pesticide,
        'sowing' : sowing,
        'termination' : termination
    }

    return data_dict


#sites:
sites_list = os.listdir(os.path.join('src' ,'sgr_data', 'data', 'raw_data'))
# remove the 'master' folder from the sites list
sites_list.remove('master')

#activities:
activities_list = os.listdir(os.path.join('src' ,'sgr_data', 'data', 'raw_data', 'master'))
activities_list = [x[:-4] for x in activities_list] #strip '.csv'
### Get the data files from upload files
#Store new data files in a nested dict based on {site: activity}
#Note that the uploadFiles module has functionality to work out if there is new data present and will sort existing from new records
activity_template_dict = {key:[] for key in activities_list}
sites_activities_dict = {key:deepcopy(activity_template_dict) for key in sites_list}


# Loop through each site and activity, call uploadFiles and store resultant dataframe
for site in sites_activities_dict:
    for activity in sites_activities_dict[site]:
        sites_activities_dict[site][activity].append(uploadFiles(site,activity))

    return 1

