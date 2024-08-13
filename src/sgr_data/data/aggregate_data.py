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

# as a basic approach the aggregate data functions:
# use a plotID to aggregate data for that plot including:
#   1. all activities including
#       1.1 activity records
#       1.2 product records for products used in each activity including price
#       1.3 activity costs using reference activity cost data tables

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
import numpy as np
from functools import reduce
import datetime

#### QUESTION: should we include plot-state data? It isn't really necessary but might help data checks

####### utility functions (export to utilities once working)

def getBasePath():
    return os.path.join('src','sgr_data','data','validated_data')

# Get site-activity data combinations
def getSiteData(site):

    base_path = getBasePath()

    ### get site directory for validated data
    site_path = os.path.join(base_path,site)
    activities_list = os.listdir(site_path) # this gets the activity folders in the validated data for the target site

    ### initialise an activities-data dictionary to hold target data
    activities_data_dict = {activity: None for activity in activities_list}

    for activity in activities_list:
        #read in validated data first
        site_activity_path = os.path.join(site_path,activity)
        activity_uploads = os.listdir(site_activity_path)

        #build up a dataframe for each activity using uploads for each of those
        for i, upload in enumerate(activity_uploads):
            site_activity_upload_path = os.path.join(site_activity_path,upload)
            if i == 0:
                activities_data_dict[activity] = pd.read_pickle(site_activity_upload_path)
            else:
                activities_data_dict[activity] = activities_data_dict[activity].append(pd.read_pickle(site_activity_upload_path), ignore_index=True)

    return activities_data_dict


# split plot id into identifying constituents
def splitPlotId(plotID):
    ### get string elements to identify plot
    str_args = plotID.split("_")

    id_dict = {
        'site' : str_args[0],
        'system' : str_args[1],
        'phase_sequence' : str_args[2],
        'rep_id' : str_args[3],
    }
    
    return id_dict


# aggregate data by plot - basic function to facilitate directed aggregations of data (e.g. by site-year replicates)
def aggregatePlotData(plotID):
    #   1. split site_activity_data into target site using splitPlotId elements
    #   2. subset each activity by plotID and store resultant DF
    #   3. generate date series on each activity
    #   4. merge activity DFs on id and date
    #   5. return resultant df for merging on a higher-level aggregation
    
    # get site for plot
    site = splitPlotId(plotID)['site']

    #get site_data
    activity_data_dict = getSiteData(site)

    # initialise a plot_data dictionary
    plot_data_dict = {activity: None for activity in activity_data_dict}
    for activity in plot_data_dict:
        #get relevant activity data for site
        activity_data = activity_data_dict[activity]
        
        #get plot data for that site/activity combination
        plot_activity_data = activity_data.loc[activity_data['plotID']==plotID,]

        #add a new date variable
        year = plot_activity_data['year']
        month = plot_activity_data['month']
        day = plot_activity_data['day']
        date_stamp = [datetime.datetime(year,month,day)]
        plot_activity_data['date'] = date_stamp

        #add as recod in plot_data_dict
        plot_data_dict[activity] = plot_activity_data

    # set as list and merge on plotID and date
    df_list = [plot_data_dict[df] for df in plot_data_dict]
    plot_data = reduce(lambda left,right: pd.merge(left,right, on = ['plotID', 'date'], how = 'outer'), df_list).fillna(pd.NA)

    return plot_data

# a more efficient aggregation function for cases where no subsetting is wanted
def aggregateAll():
    ### get site directory for validated data
    base_path = getBasePath()
    sites = os.listdir(base_path)

    #initialise data list for reduce-merge after filling the list
    data_list = []

    for site in sites:
        #get the list of activities for referent site
        activity_list = os.listdir(os.path.join(base_path,site))
        for activity in activity_list:
            #get the data files included in that activity-site combination (these are dated files)
            dates_list = os.listdir(os.path.join(base_path, site, activity))
            for dated_file in dates_list:
                file_path = os.path.join(base_path, site, activity, dated_file)
                data = pd.read_pickle(file_path)
                #add in site, activity, and entry date details to file
                nrow = data.shape[0]
                data['site'] = np.repeat(site, nrow)
                data['activity'] = np.repeat(activity, nrow)
                data['date_added'] = np.repeat(dated_file, nrow)

                #append to data_list
                data_list.append(data)
    
    #merge
    all_data = reduce(lambda left,right: pd.merge(left,right, on = ['plotID', 'date'], how = 'outer'), data_list).fillna(pd.NA)

    return all_data


## aggregation function using details such as 'system' or 'site'. 
def aggregateDataByDetail(
        sites = 'all',
        system = None,
        phase_sequence = 'all',
    ):
    
    #### select sites as a list of site-strings with options:
    # roseworthy
    # ...

    #### select whether to include phase-sequence replicates using:
    # phase_sequence = 'all' (all phase-sequence replicates included)
    # phase_sequence = 'XXX' (select the specific phase-sequences)
    # NOTE: this is ignored if a plotId is not included

    #### select whether to include base replicates
    # replicates = True - includes base replicates (exact replicates on different plots/sites)
    # replicates = False - only use if you want to generate data for a single plot

    #### plotId
    # use this in any case where you are subsetting data on a basis other than 'site'
    # ignored if sites='all', phase-sequence=True and replicates=True (this implies all data is to be aggregated)
    # exception returned if not provided and either 'phase_sequence = True' or 'replicates = True'

    # conduct exception and type checking
    if plotId == None and (phase_sequence==True or replicates==True):
        raise ValueError("You must supply a plotId if you want to return either phase_sequence replicates or replicates")
    
    if not sites == 'all':
        if not type(sites)==list:
            raise TypeError("'sites' argument must either be 'all' or a list")
        if len(sites==0):
            raise ValueError("You must specify either a list of sites or 'all' in the sites argument (default is 'all')")
        
        #check that all included sites are in the sites list
        sites_list = [
            'roseworthy',
            'kinnabulla',
            'MORE'
        ]

        sites = [site.lower() for site in sites]
        if not all(item in sites_list for item in sites):
            raise ValueError("Ensure all of your sites are included in the siteslist")
    
    ## check aggregation selection and aggregate
    if sites == 'all':
        data = aggregateAll()

    else:
        #generate a plot list (list of plotIDs)to send to 
        if phase_sequence == True:
            for site in sites:



    return data


## aggregate replicates by plot ID
def aggregateDataByPlot(
        plotId,
        sites = 'own',
        phase_sequence = 'plot',
        replicates = True
    ):
    
    #### select sites as a list of site-strings with options:
    # roseworthy
    # ...
    # if default of 'own' then only the site that the plot is in is used

    #### select whether to include phase-sequence replicates using:
    # phase_sequence = 'all' (all phase-sequence replicates included)
    # phase_sequence = 'plot' (only the phase-sequences that are the same as the sequence for the plot)

    #### select whether to include base replicates
    # replicates = True - includes base replicates (exact replicates on different plots/sites)
    # replicates = False - only use if you want to generate data for a single plot

    # conduct exception and type checking
    if plotId == None:
        raise ValueError("You must supply a plotId")
    
    if not sites == 'all' or not sites == 'own':
        if not type(sites)==list:
            raise TypeError("'sites' argument must either be 'all' or 'own'")

    if phase_sequence == 'all' and replicates == False:
        Warning("phase_sequence = 'all' implies that replicates = True")

    if replicates == False:
        #return own data omly



    return data



