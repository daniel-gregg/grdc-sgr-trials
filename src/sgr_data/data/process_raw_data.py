### Uses the upload package to upload new data saved in 'sgr/sgr_data/data/raw_data/'
### Passes new date entries through the relevant validators
### Saves new data to relevant dataframes if validation passes

# base imports
from pyprojroot.here import here
import sys
import asyncio
import os
import pandas as pd
import csv 
from copy import deepcopy

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.sgr_data.upload.upload import uploadFiles
#from src.sgr_data.validate.validate import validateData

### list sites and activities in the raw_data file


#sites:
sites_list = os.listdir(os.path.join('src' ,'sgr_data', 'data', 'raw_data'))
# remove the 'master' folder from the sites list
sites_list.remove('master')

#activities:
activities_list = os.listdir(os.path.join('src' ,'sgr_data', 'data', 'raw_data', 'master'))
print(activities_list)
activities_list = [x[:-3] for x in activities_list] #strip '.csv'
print(activities_list)

### Get the data files from upload files
#Store new data files in a nested dict based on {site: activity}
#Note that the uploadFiles module has functionality to work out if there is new data present and will sort existing from new records
activity_template_dict = {key:[] for key in activities_list}
sites_activities_dict = {key:deepcopy(activity_template_dict) for key in sites_list}


#now loop through each site and activity, call uploadFiles and store resultant dataframe
for site in sites_activities_dict:
    for activity in sites_activities_dict[site]:
        sites_activities_dict[site][activity].append(uploadFiles(site,activity))

print(sites_activities_dict)

