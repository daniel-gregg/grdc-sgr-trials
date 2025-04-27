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
    return os.path.join('src','sgr_data','data')

# for each call on getting activity data this returns an activity cost record
def getActivityCostsData(activity, year):
    #note if year not present the function defaults to returning the nearest year record
    # no warning is given as only 2020-21 records are currently available

    #read in activity cost data from reference data
    base_path = getBasePath()
    reference_data_path = os.path.join(base_path, 'reference_data', 'ActivitiesCosts.csv')

    #load .csv data
    activity_data = pd.read_csv(reference_data_path)

    #acivity mapping
    activity_mapping_dict = {
        'fertiliser' : 'FERT_SPREADING_HA',
        'fungicide' : 'GROUND_SPRAYING_HA',
        'herbicide' : 'GROUND_SPRAYING_HA',
        'pesticide' : 'GROUND_SPRAYING_HA',
        'termination' : 'HARVEST_HA',
        'sowing' : 'SOWING',
    }

    #set activity string to reference activity_data columns
    activity_string = activity_mapping_dict[activity]

    #get values - these are by year
    activity_value = activity_data.loc[activity_data['FY_END']==year,][activity_string].item()

    if pd.isna(activity_value):
        #return average instead
        activity_value = np.nanmean(activity_data[activity_string])
    
    return activity_value


# Get site-activity data combinations
def getSiteData(site):

    base_path = getBasePath()

    ### get site directory for validated data
    site_path = os.path.join(base_path, 'validated_data', site)
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

#use the product and activity to get the product price
def getProductPrice(product, activity):
    #returns a product price to use to calculate product costs for an activity
    #   some values are empty or NA - in these cases it returns an average
    product = product.lower().strip()

    base_path = getBasePath()

    # set up a product-file mapping to activities
    product_file_dict = {
        'fertiliser': 'FertProductData.csv',
        'fungicide' : 'FungProductData.csv',
        'herbicide' : 'HerbProductData.csv',
        'pesticide' : 'PestProductData.csv',
    }

    #get product data path
    product_data_path = os.path.join(base_path, 'reference_data', product_file_dict[activity])
    
    #load the .csv
    product_data = pd.read_csv(product_data_path)
    product_names = [x.lower().strip() for x in product_data['name']] #strip whitespace
    select_bool = [x == product.lower().strip() for x in product_names]
    #find the product in the file and return the price - this must exist because it has been validated already
    product_price = product_data.loc[select_bool]['price'].item()

    # replace missing data with average noting that '0' is NOT missing
    if pd.isna(product_price) or product_price == None:
        #get all prices
        product_price = np.nanmean(
            product_data['price']
        )

    #return the price
    return product_price

#use crop name and reference data ('CropPriceData.csv') to get crop prices
def getCropPrice(crop, price_type):
    #price must be one of the options in the columns of the CropPriceData.csv file. 
    # currently these are:
    # prices_ma5
    # prices_2022

    base_path = getBasePath()
    crop_file_path = os.path.join(base_path, 'reference_data', 'CropPriceData.csv')
    
    crop_price_data = pd.read_csv(crop_file_path)

    #strip and lower-case the strings
    crop_names_list = [x.lower().strip() for x in crop_price_data['name']]
    crop_name = crop.lower().strip()

    #use a boolean list to select correct row
    select_bool = [x == crop_name for x in crop_names_list]
    if not any(select_bool): #no match found - print exception with crop name
        raise ValueError('The terminated crop {} is not in the crops list. Ensure consistent naming'.format(crop))

    crop_price = crop_price_data.loc[select_bool][price_type].item()/1000 #prices are in tonnes, yield are in kilograms
    
    return crop_price


# a more efficient aggregation function for cases where no subsetting is wanted
def aggregateAll(price_type = 'prices_ma5'):
    #price_type is one of the column headers in '../reference_data/CropPriceData.csv'
    #   it defaults to a 5 year moving average of crop prices. 


    ### get site directory for validated data
    base_path = getBasePath()
    site_path = os.path.join(base_path, 'validated_data')
    sites = os.listdir(site_path)

    #initialise data list for reduce-merge after filling the list
    data_fertiliser_list = []
    data_fungicide_list = []
    data_herbicide_list = []
    data_pesticide_list = []
    data_crops_sowing_list = []
    data_crops_termination_list = []

    for site in sites:
        #get the list of activities for referent site
        activity_list = os.listdir(os.path.join(site_path,site))
        for activity in activity_list:
            #get the data files included in that activity-site combination (these are dated files)
            dates_list = os.listdir(os.path.join(site_path, site, activity))

            #check if empty, if so continue
            if len(dates_list) == 0:
                continue
            
            #else get pickle files and merge
            for dated_file in dates_list:

                # get file path and data for site-activity-date(uploaded) combinations
                file_path = os.path.join(site_path, site, activity, dated_file)
                data = pd.read_pickle(file_path)
                nrow = data.shape[0]

                # add in fixed (site-activity) variables
                data['site'] = np.repeat(site, nrow)
                data['activity_type'] = np.repeat(activity, nrow)
                
                # then add in vars that change by year (date and potentially activity cost)
                dates = []
                activity_cost = []
                product_costs = []
                product_qty = []
                revenue_dollars = []

                for row in range(data.shape[0]):

                    #get date
                    year = data.iloc[row]['year']
                    month = data.iloc[row]['month']
                    day = data.iloc[row]['day']
                    dates.append(datetime.datetime(year, month, day))
                    
                    #get activity cost
                    activity_cost.append(getActivityCostsData(activity, year))

                    #get product cost - check if a product using activity
                    if activity == 'sowing' or activity == 'termination':
                        product_costs.append(0)
                    else:    
                        product = data.iloc[row]['name']
                        print('product for product price is {} at site {}'.format(product, site))
                        product_price = getProductPrice(product, activity)
                        product_qty = data.iloc[row]['appliedAmount'].item()
                        product_costs.append(np.multiply(product_price, product_qty))

                    #if activity is termination, get yield and revenue
                    if not activity == 'termination':
                        revenue_dollars.append(0)
                    else:
                        crop1 = data.iloc[row]['crop1Name']
                        crop2 = data.iloc[row]['crop2Name']
                        crop3 = data.iloc[row]['crop3Name']
                        print('crop 1 is {} at site {}'.format(crop1, site))
                        print('crop 2 is {} at site {}'.format(crop2, site))
                        print('crop 3 is {} at site {}'.format(crop3, site))
                        if pd.isna(crop1):
                            price1 = 0
                            yield1 = 0
                        else:
                            price1 = getCropPrice(crop1, price_type)
                            yield1 = data.iloc[row]['crop1Yield']
                        if pd.isna(crop2):
                            price2 = 0
                            yield2 = 0
                        else:
                            price2 = getCropPrice(crop2, price_type)
                            yield2 = data.iloc[row]['crop2Yield']
                        if pd.isna(crop3):
                            price3 = 0
                            yield3 = 0
                        else:
                            price3 = getCropPrice(crop3, price_type)
                            yield3 = data.iloc[row]['crop3Yield']

                        revenue_dollars.append(
                            yield1 * price1 +
                            yield2 * price2 + 
                            yield3 + price3
                        )

                data['date'] = dates
                data['costs_activity_dollars'] = activity_cost
                data['costs_product_applied_dollars'] = product_costs
                data['revenue_crops_dollars'] = revenue_dollars

                #append to data_list for merging later using 'reduce'
                if activity == 'fertiliser':
                    data_fertiliser_list.append(data)
                if activity == 'fungicide':
                    data_fungicide_list.append(data)
                if activity == 'herbicide':
                    data_herbicide_list.append(data)
                if activity == 'pesticide':
                    data_pesticide_list.append(data)
                if activity == 'sowing':
                    data_crops_sowing_list.append(data)
                if activity == 'termination':
                    data_crops_termination_list.append(data)
    
    #concatenate data (of same types)
    crop_sowing_data = pd.concat(data_crops_sowing_list)
    crop_termination_data = pd.concat(data_crops_termination_list)

    fertiliser_data = pd.concat(data_fertiliser_list)
    fungicide_data = pd.concat(data_fungicide_list)
    herbicide_data = pd.concat(data_herbicide_list)
    pesticide_data = pd.concat(data_pesticide_list)

    #merge crop (sowing/termination) data
    data_crops_list = [crop_sowing_data, crop_termination_data]
    crop_data = reduce(
        lambda left, right: pd.merge(
            left, right, on = [
                'plotID', 
                'date', 
                'activity_type', 
                'site', 
                'crop1Name',
                'crop2Name',
                'crop3Name',
                'year', 
                'month', 
                'day', 
                'costs_activity_dollars', 
                'costs_product_applied_dollars',
                'revenue_crops_dollars',
                'comments'
                ], 
            how = 'outer'), 
        data_crops_list).fillna(pd.NA)

    #merge non-crop data
    non_crop_data_list = [
        fertiliser_data,
        fungicide_data,
        herbicide_data,
        pesticide_data
    ]

    non_crop_data = reduce(
        lambda left,right: pd.merge(
            left,right, on = [
                'plotID', 
                'date', 
                'activity_type', 
                'revenue_crops_dollars',
                'costs_product_applied_dollars',
                'costs_activity_dollars',
                'unitsAppliedKgOrLitres',
                'appliedAmount',
                'site', 
                'year', 
                'month', 
                'day', 
                'name',
                'comments'
                ], 
            how = 'outer'), 
        non_crop_data_list).fillna(pd.NA)

    #merge crop and non-crop data
    all_data = crop_data.merge(non_crop_data, how = 'outer')

    #save all_data to file
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    filepath = os.path.join('src','sgr_data','processed_data', today+'.csv')
    all_data.to_csv(filepath)

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
    if not sites == 'all':
        if not type(sites)==list:
            raise TypeError("'sites' argument must either be 'all' or a list")
        if len(sites==0):
            raise ValueError("You must specify either a list of sites or 'all' in the sites argument (default is 'all')")
        
        #check that all included sites are in the sites list
        sites_list = [
            'roseworthy',
            'kinnabulla',
            'edillilie',
            'streatham',
            'wallup',
            'manang',
            'appila',
            'hart',
        ]

        sites = [site.lower() for site in sites]
        if not all(item in sites_list for item in sites):
            raise ValueError("Ensure all of your sites are properly spelt")
    
    ## check aggregation selection and aggregate
    if sites == 'all':
        data = aggregateAll()

    else:
        #generate a plot list (list of plotIDs)to send to 
        #COMPLETE THIS LATER
        x=1 #fill later

    return data


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

    #initialise a dataframe for new variables to merge later
    df_type_cost = {
        'plotID' : [],
        'site' : [],
        'date' : [],
        'activity_type' : [],
        'activity_cost' : [],
    }

    # initialise a plot_data dictionary
    plot_data_dict = {activity: None for activity in activity_data_dict}
    for i, activity in enumerate(plot_data_dict):
        #get relevant activity data for site
        activity_data = activity_data_dict[activity]
        
        #get plot data for that site/activity combination
        plot_activity_data = activity_data.loc[activity_data['plotID']==plotID,]

        # plot_activity_data can be more than one row or be empty.
        if plot_activity_data.empty:
            continue

        if plot_activity_data.shape[0] == 1:

            #add a new date variable
            year = plot_activity_data['year']
            month = plot_activity_data['month']
            day = plot_activity_data['day']
            date_stamp = [datetime.datetime(year,month,day)]
            plot_activity_data['date'] = date_stamp

            #add target variables to type_cost dataframe
            df_type_cost['plotID'].append(plotID)
            df_type_cost['date'].append(date_stamp)
            df_type_cost['activity_type'].append(activity)
            df_type_cost['activity_cost'].append(getActivityCostsData(activity, year))

        if plot_activity_data.shape[0] > 0:
            dates = []
            for activity_date in range(plot_activity_data.shape[0]):
                year = plot_activity_data.iloc[activity_date,]['year']
                month = plot_activity_data.iloc[activity_date,]['month']
                day = plot_activity_data.iloc[activity_date,]['day']
                date_stamp = datetime.datetime(year,month,day)
                dates.append(date_stamp)

                #add target variables to type_cost dataframe
                df_type_cost['plotID'].append(plotID)
                df_type_cost['site'].append(site)
                df_type_cost['date'].append(date_stamp)
                df_type_cost['activity_type'].append(activity)
                df_type_cost['activity_cost'].append(getActivityCostsData(activity, year))
            
            #append dates
            plot_activity_data['date'] = dates

        #add plot_activity_data as record in plot_data_dict
        plot_data_dict[activity] = plot_activity_data

    # set as list and merge on plotID and date
    df_list = [plot_data_dict[df] for df in plot_data_dict]
    df_list.append(df_type_cost)
    plot_data = reduce(lambda left,right: pd.merge(left,right, on = ['plotID', 'date'], how = 'outer'), df_list).fillna(pd.NA)

    return plot_data

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
        #return own data only
        x=1

    return 1



aggregateAll()