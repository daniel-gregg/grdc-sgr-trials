### Calls the upload modules based on raw data
### Finds new data entries and uploads those

# base imports
from pyprojroot.here import here
import sys
import os
import pandas as pd 

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

#activity can be one of:
    #   fertiliser
    #   fungicide
    #   herbicide
    #   insecticide
    #   pesticide
    #   sowing
    #   termination

#site can be one of:
    #roseworthy
    # ADD MORE

### utilities

#base path
base_path = os.path.join('src' ,'sgr_data', 'data')

# Async function to get data based on a provided filepath
def getCSV(filePath):
    df_ = pd.read_csv(filePath)
    return df_

# Get existing files - REPLACE THIS WTIH DB GET QUERY WHEN CONNECTING TO DB
def getExistingFiles(path):
    existing_files = os.listdir(path)

    #This is a dictionary of activities (see above) as keys with values a list of dates (indicating existing data entries)
    return existing_files

# Get raw data files list - REDUNDANT IN THE FUTURE AS DON'T NEED TO DIFFERENCE
def getRawFilesList(path):
    raw_files = os.listdir(path)

    raw_files = [x.rstrip('.csv') for x in raw_files] #strip '.csv'

    #This returns a list of dates without the '.csv' appended
    return raw_files

# Define the list of new files to upload (identified by date)
def getFilesToUpload(existing,raw):
    upload_files = list(set(raw).difference(set(existing)))

    return upload_files

#Main action (upload) function
def uploadFiles(site, activity):

    raw_data_path = os.path.join(base_path, 'raw_data', site, activity)
    existing_data_path = os.path.join(base_path, 'processed_data', 'upload_records', site, activity)

    #get existing data record
    existing_data = getExistingFiles(existing_data_path)

    #get raw data files
    raw_files = getRawFilesList(raw_data_path)

    #get files to upload (those not currently existing)
    upload_files_list = getFilesToUpload(existing=existing_data, raw = raw_files)

    #If no new data return None
    if len(upload_files_list) == 0:
        return None
    #Else upload data into list of pandas dfs
    else:
        data = {}
        for file in upload_files_list:
            #file_name = upload_files_list[file]
            path_name = os.path.join(raw_data_path,file+'.csv')
            df = getCSV(path_name)
            data[file] = df
        
        return data

    
