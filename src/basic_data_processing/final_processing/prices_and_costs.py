
## Final processing of basic field data
# This function integrates external/reference data and creates a final structured dataframe that provides all relevant
# data for further analysis (e.g. prices, measures (of state), events, etc)

# currently only prices are integrated.
# future work will also integrate:
#   1. measures of states (e.g. soil moisture)
#   2. externally-derived measurements such as rainfall, rainfall intensity, VPD high/extreme days per month, etc.
#   3. other measures/data as it becomes available

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

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

import pandas as pd
import numpy as np
from functools import reduce
import datetime

from src.utils.base_paths import get_reference_data_path
from src.utils.base_paths import get_validated_data_path
from src.utils.base_paths import get_processed_data_path


# for each call on getting activity data this returns an activity cost record
def getActivityCostsData(activity, year):
    #note if year not present the function defaults to returning the nearest year record
    # no warning is given as only 2020-21 records are currently available

    #read in activity cost data from reference data
    reference_data_path = get_reference_data_path('ActivitiesCosts.csv')

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


#use the product and activity to get the product price
def getProductPrice(product, activity):
    #returns a product price to use to calculate product costs for an activity
    #   some values are empty or NA - in these cases it returns an average
    product = product.lower().strip()

    # set up a product-file mapping to activities
    product_file_dict = {
        'fertiliser': 'FertProductData.csv',
        'fungicide' : 'FungProductData.csv',
        'herbicide' : 'HerbProductData.csv',
        'pesticide' : 'PestProductData.csv',
    }

    #get product data path
    product_data_path = get_reference_data_path(product_file_dict[activity])
    
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

    crop_file_path = get_reference_data_path('CropPriceData.csv')
    
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


# process all data integrating target price series
def integratePricesAndCosts(price_type = 'prices_ma5'):
    #price_type is one of the column headers in '../reference_data/CropPriceData.csv'
    #   it defaults to a 5 year moving average of crop prices. 

    ## Note: we subset data by id, date and the following groupings of activities:
    #   Sowing
    #   Harvest/termination
    #   Fertiliser applications
    #   Pesticide, Herbicide and/or Fungicide applications
    # The latter are all grouped together as they are mixed in a single tank in the 'real world'
    # We group them together to ensure that activity costs are not over-allocated in instances of grouped activities
    # Product costs are still individually accounted for

    ### get site directory for validated data
    site_path = get_validated_data_path()
    sites = os.listdir(site_path)

    #initialise data list for reduce-merge after filling the list
    data_fertiliser_list = []
    data_fungicide_list = []
    data_herbicide_list = []
    data_pesticide_list = []
    data_crops_sowing_list = []
    data_crops_termination_list = []

    for site in sites:
        #list activities:
        activity_list = os.listdir(get_validated_data_path(site))
        for activity in activity_list:
            dates_list = os.listdir(get_validated_data_path(site, activity))

            #check if empty, if so continue
            if len(dates_list) == 0:
                continue
            
            #else get pickle files and merge
            for dated_file in dates_list:

                # get file path and data for site-activity-date(uploaded) combinations
                file_path = os.path.join(get_validated_data_path(site, activity), dated_file)
                data = pd.read_pickle(file_path)
                nrow = data.shape[0]

                # add in fixed (site-activity) variables
                data['site'] = np.repeat(site, nrow)
                data['activity_type'] = np.repeat(activity, nrow)
                
                # then add in vars that change by year (date and potentially activity cost)
                ids = []
                activities = []
                dates = []
                activity_cost = []
                product_costs = []
                product_qty = []
                revenue_dollars = []

                for row in range(data.shape[0]):

                    #get date - this is used to ensure product applications that occur in the same effort
                    #   are allocated to a single 'activity' (so no double counting of activity costs)
                    year = data.iloc[row]['year']
                    month = data.iloc[row]['month']
                    day = data.iloc[row]['day']
                    dates.append(datetime.datetime(year, month, day))
                    ids.append(data.iloc[row]['plotID'])
                    activities.append(activity)
                    
                    ### allocate activity costs
                    #check if id, date and activity are same as last to ensure no double counting of activities
                    
                    # the first iteration case
                    if row == 0:
                        activity_cost.append(float(getActivityCostsData(activity, year)))
                    else:
                        # the same-activity case for a given plot
                        if ids[row] == ids[row-1] and activities[row] == activities[row-1] and dates[row] == dates[row-1]:
                            activity_cost.append(float(0))
                        # the different activity case for a given plot
                        else:
                            activity_cost.append(float(getActivityCostsData(activity, year)))


                    #get product cost - check if a product using activity
                    if activity == 'sowing' or activity == 'termination':
                        product_costs.append(float(0))
                    else:    
                        data.loc[row,'appliedAmount'] = float(data.iloc[row]['appliedAmount'])
                        product = data.iloc[row]['name']
                        print('product for product price is {} at site {}'.format(product, site))
                        product_price = float(getProductPrice(product, activity))
                        product_qty = float(data.iloc[row]['appliedAmount'])
                        product_costs.append(np.multiply(float(product_price), float(product_qty)))

                    #if activity is termination, get yield and revenue
                    if not activity == 'termination':
                        revenue_dollars.append(float(0))
                    else:
                        crop1 = data.iloc[row]['crop1Name']
                        crop2 = data.iloc[row]['crop2Name']
                        crop3 = data.iloc[row]['crop3Name']
                        print('crop 1 is {} at site {}'.format(crop1, site))
                        print('crop 2 is {} at site {}'.format(crop2, site))
                        print('crop 3 is {} at site {}'.format(crop3, site))
                        if pd.isna(crop1):
                            price1 = float(0)
                            yield1 = float(0)
                        else:
                            price1 = float(getCropPrice(crop1, price_type))
                            yield1 = float(data.iloc[row]['crop1Yield'])
                        if pd.isna(crop2):
                            price2 = float(0)
                            yield2 = float(0)
                        else:
                            price2 = float(getCropPrice(crop2, price_type))
                            yield2 = float(data.iloc[row]['crop2Yield'])
                        if pd.isna(crop3):
                            price3 = float(0)
                            yield3 = float(0)
                        else:
                            price3 = float(getCropPrice(crop3, price_type))
                            yield3 = float(data.iloc[row]['crop3Yield'])

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

    # set fertiliser_data['appliedAmount'] astype(float) - for some reason it is not converting in the above
    fertiliser_data['appliedAmount'] = fertiliser_data['appliedAmount'].astype(float)

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

    # merge crop and non-crop data
    all_data = crop_data.merge(non_crop_data, how = 'outer')

    # set obserations id
    all_data['observation_id'] = np.arange(all_data.shape[0])

    ### clean up data - remove duplicates of activity costs (operational, not product costs)
    
    # sort data by date
    all_data = all_data.sort_values(by=['date'],axis=0, ascending=True)
    
    # subset only for target aggregation activities
    subdat_activities = all_data[all_data['activity_type'].isin(['herbicide', 'pesticide', 'fungicide'])]

    # then loop through each row checking for conditions to set activity costs to zero
    for site in sites:
        #subset data by site
        subdat_site = subdat_activities.loc[subdat_activities['site']==site,]

        #subset by plot
        plots = [*set(subdat_site['plotID'])]
        
        for plot in plots:
            subdat_plot = subdat_site.loc[subdat_site['plotID']==plot]

            site_dates = [*set(subdat_plot['date'])]

            # loop through dates for site to check for conditions met for resetting of activity costs to zero
            for site_date in site_dates:
                subdat_plot_date = subdat_plot.loc[subdat_plot['date'] == site_date]
                if subdat_plot_date.shape[0] < 2:
                    # only one activity in date set so continue
                    continue
                #remaining observations at this point would be aggregated into a single activity
                # get observation (row) ids for the full dataset and set all but one to zero
                obs_id_list = [*subdat_plot_date['observation_id']]

                # check that ALL elements for costs_activity_dollars are the same - warn if not
                if len(set(all_data.loc[obs_id_list,'costs_activity_dollars'])) > 1:
                    Warning(f'activity costs for site {site}, plotid {plot} and date {site_date} are not all the same - they need to be for aggregation')

                obs_id_list.pop()
                for element in range(len(obs_id_list)):
                    all_data.loc[obs_id_list,'costs_activity_dollars'] = 0


    ### save all_data to file
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    filepath = os.path.join(get_processed_data_path(), today+'.csv')
    all_data.to_csv(filepath)

    return all_data
