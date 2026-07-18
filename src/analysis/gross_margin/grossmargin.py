'''
    A module to calculate/simulate gross margins for a farm enterprise
    Users can:
        * Use default data (TBD) to generate gross margin simulations for selected enterprises/regions (currently just cropping)
        * Specify data to be used including prices, input quantities, output/yield levels and regions
        * Choose to obtain a single estimate or to simulate a chosen number of draws to obtain a distribution of GM outcomes
    The module returns:
        * A Gross margin estimate or vector of estimates
'''

'Python imports'

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

'Custom imports'
'TBD - this is for additional modules'

from src.utils.base_paths import get_processed_data_path
from src.utils.base_paths import get_reference_data_path
from src.utils.aggregation_utilities import getProcessedDataList
from src.utils.base_paths import get_gross_margin_data_path


def getStateChangeIndex(series):
    """
    Function to get the index of sequential states
    This is used to identify the entirety of a state (i.e. FALLOW or CROP).
    """
    for i in range(1, len(series)):
        if series[i] != series[i - 1]:
            return i-1
    return None  # No state change found

def getCropSequenceIndex(states):
    # returns the index of the first crop sequence in the supplied data

    #if dat['state'].iloc[0] != 'FALLOW':
    #    raise ValueError("Data must start with a FALLOW state")

    # set the starting state
    starting_state = states[0]

    # if the starting state is FALLOW, then the sequence should be FALLOW, CROP, FALLOW
    if starting_state == 'FALLOW':
        end_of_pre_fallow_state = getStateChangeIndex(states)
        #check that there remain both FALLOW and CROP states after the first FALLOW state
        if ('CROP' not in states[end_of_pre_fallow_state:]) and ('FALLOW' not in states[end_of_pre_fallow_state:]):
            raise ValueError("There is no full crop sequence in the data")

        crop_start_index = end_of_pre_fallow_state + 1
        crop_end_index = getStateChangeIndex(states[crop_start_index:]) + crop_start_index + 1

    else:
        end_of_pre_fallow_state = None
        crop_start_index = 0
        crop_end_index = getStateChangeIndex(states) + 1

    return ({
        'starting_state': starting_state,
        'end_of_pre_fallow_state': end_of_pre_fallow_state,
        'crop_start_index': crop_start_index,
        'crop_end_index': crop_end_index,
    })

def genStateSeriesToMatchProcessedData(dat):
    """
    Function to generate a state series that matches the processed data.
    plotStateData only records state at change of state date
    processed_data has many entries based on the date of an activity (not necessarily a state change)
    We need a series of state that is 'filled in' to match the processed data

    Key issues are that:
    - all activities matching the date of a state/state change must have that state
        - this can be an issue when several activities are recorded on the same date but the state change is not the first of these
    """

    # note that this ONLY works for a data file with a single plot
    if len(dat['plotID'].unique()) > 1:
        raise ValueError("Data must contain only one plot")

    # Get the plot state data
    plot_state_data = pd.read_csv(get_reference_data_path('PlotStateData.csv'))
    plot_state_data = plot_state_data[['PLOT_ID', 'DATE', 'STATE']]
    plot_state_data['DATE'] = pd.to_datetime(plot_state_data['DATE'], format = 'mixed')

    # subset plot_state_data to match the plotID in dat
    current_plot_id = dat['plotID'].iloc[0]
    plot_state_data = plot_state_data[plot_state_data['PLOT_ID'] == current_plot_id]

    # guard: no matching state data for this plot (commonly a plotID mismatch,
    # e.g. a stray whitespace difference between the processed data and PlotStateData.csv)
    if plot_state_data.empty:
        raise ValueError(
            f"No plot state data found for plotID '{current_plot_id}'. "
            "Check that the plotID in the processed data exactly matches a PLOT_ID "
            "in PlotStateData.csv (watch for stray whitespace)."
        )

    # order plot_state_data by date
    plot_state_data = plot_state_data.sort_values(by='DATE')

    # check that plot_state_data starts with a FALLOW state
    if plot_state_data['STATE'].iloc[0] != 'FALLOW':
        raise ValueError("Plot state data must start with a FALLOW state")

    # initialise the state series with the first state
    # this is the first state in the plot_state_data
    initial_state = plot_state_data['STATE'].iloc[0]

    #initialise state series
    state = []

    for index, row in dat.iterrows():
        # get the row date
        date = pd.to_datetime(row['date'])

        #check the date against the plot_state_data allowing for dates before the first state change
        # and after the last state change
        if date < plot_state_data['DATE'].iloc[0]:
            # If the date is before the first state change, use the initial state
            state.append(initial_state)
            continue

        # else get the latest entry in plot_state_data that is equal to or before the date
        current_state = plot_state_data[plot_state_data['DATE'] <= date].tail(1)
        if not current_state.empty:
            state.append(current_state['STATE'].values[0])
            continue

        # If the date is after the last state change, use the last state
        if date > max(plot_state_data['DATE']):
            state.append(plot_state_data['STATE'].iloc[-1])
            continue

    # merge state series with dat
    dat['state'] = state

    return dat

def checkExistenceOfCropState(states_list):
    """
    Function to check if there is a crop state in the data (returns True).
    If there is no crop state return False.

    All plots start with an initialising Fallow state. This needs to be removed to check
    if remaining states move from CROP to FALLOW at least once.
    """

    # check if states_list starts with FALLOW
    if states_list[0] == 'FALLOW':

        # check if ALL states are FALLOW
        if all(state == 'FALLOW' for state in states_list):
            return False
        # remove initial FALLOW states using index from getStateChangeIndex
        initial_fallow_index = getStateChangeIndex(states_list)
        states_list = states_list[initial_fallow_index + 1:]

    ### now check that the remaining sequence is CROP then STATE

    # check if empty
    if not states_list:
        return False

    # check that there remains a FALLOW entry in the states_list
    if 'FALLOW' not in states_list:
        return False

    # else all good - there are both CROP and FALLOW states in the data, so there is a crop sequence
    return True

def getCropSequenceGrossMargin():
    """
    Function to calculate gross margin for a crop sequence.
    """

    # get processed data files list
    processed_data_list = getProcessedDataList()

    # Loop through each processed data file
    # loop through to read in
    for file in processed_data_list:
        filepath = os.path.join(get_processed_data_path(), file)
        data = pd.read_csv(filepath)

        ## append dates to data file using year, month and day columns
        data['date'] = pd.to_datetime(data[['year', 'month', 'day']])

        # reset data index
        data.reset_index(drop=True, inplace=True)

        #initialise arrays
        operational_costs_dollars = []
        material_input_costs_dollars = []
        revenue_dollars = []
        gross_margin_dollars = []
        sites_list = []
        plots_list = []
        years_list = []
        crop_sequence_number = []
        crop_1_name = []
        crop_2_name = []
        crop_3_name = []
        crop_1_yield = []
        crop_2_yield = []
        crop_3_yield = []

        # subset by site and plot
        sites = [*set(data['site'])]

        for site in sites:
            subdat_site = data.loc[data['site'] == site,]

            #get plots and subset
            plots = [*set(subdat_site['plotID'])]

            for plot in plots:

                # check if 'BUFFER' is in the plotID - BUFFER plots are not real plots and should be excluded from the analysis
                if 'BUFFER' in plot:
                    # skip this plot
                    continue

                # Subset the data for the plot using plotID
                subdat_plot = subdat_site.loc[subdat_site['plotID'] == plot]

                # Order the data by date
                subdat_plot = subdat_plot.sort_values(by=['year', 'month', 'day'])

                subdat_plot = genStateSeriesToMatchProcessedData(subdat_plot)

                # Check if the plot has a crop sequence (i.e. There is a 'CROP' sequence followed by at least one 'FALLOW' state)
                if not (checkExistenceOfCropState(subdat_plot['state'].tolist())):
                    sites_list.append(site)
                    plots_list.append(plot)
                    years_list.append('NA')

                    operational_costs_dollars.append('NA')
                    material_input_costs_dollars.append('NA')
                    revenue_dollars.append('NA')
                    gross_margin_dollars.append('NA')

                    crop_sequence_number.append('NA')
                    crop_1_name.append('NA')
                    crop_2_name.append('NA')
                    crop_3_name.append('NA')
                    crop_1_yield.append('NA')
                    crop_2_yield.append('NA')
                    crop_3_yield.append('NA')

                    continue

                else:
                    # while there is a complete crop sequence left in subdat_plot, calculate gross margin
                    # initialise crop sequence number
                    crop_sequence_ind = 1

                    while checkExistenceOfCropState(subdat_plot['state'].tolist()):
                        # A crop sequence starts from immediately after harvest (i.e. 'FALLOW') state and
                        # ends upon next harvest
                        # so a crop sequence will look like this in the state variable:
                        # FALLOW, FALLOW, ..., FALLOW, CROP, CROP, ..., CROP, [FALLOW]
                        # Where the last FALLOW is not included in this crop sequence
                        # Also note that ALL plots start in a FALLOW state
                        crop_sequence = getCropSequenceIndex(subdat_plot['state'].tolist())
                        # get final data frame including cost and revenue components
                        subdat_plot_crop = subdat_plot.iloc[0:crop_sequence['crop_end_index']+1] #pandas: start index is inclusive, end index is exclusive

                        # calculate crop gross margin inputs
                        operating_costs = float(np.sum(subdat_plot_crop['costs_activity_dollars']))
                        material_costs = float(np.sum(subdat_plot_crop['costs_product_applied_dollars']))
                        gross_revenue = float(np.sum(subdat_plot_crop['revenue_crops_dollars']))

                        sites_list.append(site)
                        plots_list.append(plot)

                        # create the year index based on year sown.
                        years_list.append(subdat_plot_crop['year'].iloc[crop_sequence['crop_start_index']])

                        operational_costs_dollars.append(operating_costs)
                        material_input_costs_dollars.append(material_costs)
                        revenue_dollars.append(gross_revenue)
                        gross_margin_dollars.append(gross_revenue - operating_costs - material_costs)
                        crop_sequence_number.append(crop_sequence_ind)

                        # get crop names
                        crop_1_n = subdat_plot_crop['crop1Name']
                        crop_2_n = subdat_plot_crop['crop2Name']
                        crop_3_n = subdat_plot_crop['crop3Name']

                        # need to remove empty and NaN entries
                        crop_1_n = [name for name in crop_1_n if pd.notna(name) and name != '']
                        crop_2_n = [name for name in crop_2_n if pd.notna(name) and name != '']
                        crop_3_n = [name for name in crop_3_n if pd.notna(name) and name != '']

                        # then add first element in
                        crop_1_name.append(crop_1_n[0] if crop_1_n else 'NA')
                        crop_2_name.append(crop_2_n[0] if crop_2_n else 'NA')
                        crop_3_name.append(crop_3_n[0] if crop_3_n else 'NA')

                        # get crop yields
                        crop_1_y = subdat_plot_crop['crop1Yield']
                        crop_2_y = subdat_plot_crop['crop2Yield']
                        crop_3_y = subdat_plot_crop['crop3Yield']

                        # need to remove empty and NaN entries in yields first
                        crop_1_y = [y for y in crop_1_y if pd.notna(y) and y != '']
                        crop_2_y = [y for y in crop_2_y if pd.notna(y) and y != '']
                        crop_3_y = [y for y in crop_3_y if pd.notna(y) and y != '']

                        # then add first element in
                        crop_1_yield.append(crop_1_y[0] if crop_1_y else 'NA')
                        crop_2_yield.append(crop_2_y[0] if crop_2_y else 'NA')
                        crop_3_yield.append(crop_3_y[0] if crop_3_y else 'NA')

                        # remove the crop sequence from the subdat_plot
                        subdat_plot = subdat_plot.iloc[crop_sequence['crop_end_index'] + 1:] #pandas shite - start index is inclusive, end index is exclusive

                        #check if empty
                        if subdat_plot.empty:
                            break # there is no more data in this series
                        crop_sequence_ind += 1 #iterate the crop_sequence_ind ready for next loop

        gm_df = pd.DataFrame({
            'site' : sites_list,
            'plot' : plots_list,
            'year' : years_list,
            'crop_sequence' : crop_sequence_number,
            'operational_costs_dollars' : operational_costs_dollars,
            'material_input_costs_dollars' : material_input_costs_dollars,
            'crop_1_name' : crop_1_name,
            'crop_2_name' : crop_2_name,
            'crop_3_name' : crop_3_name,
            'crop_1_yield' : crop_1_yield,
            'crop_2_yield' : crop_2_yield,
            'crop_3_yield' : crop_3_yield,
            'plot_revenue_dollars' : revenue_dollars,
            'plot_gross_margin_dollars' : gross_margin_dollars
        })

        # write to file with processed file date- use different folders for different GM processing dates to separate iterations
        date_string = datetime.datetime.now().strftime("%d_%m_%Y")
        dir_path_gm_csv = get_gross_margin_data_path(date_string)
        if os.path.exists(dir_path_gm_csv):
            gm_df.to_csv(os.path.join(dir_path_gm_csv, file))
        else:
            os.mkdir(dir_path_gm_csv)
            gm_df.to_csv(os.path.join(dir_path_gm_csv, file))


def getGrossMarginSensitivityToCropPrices():
    """
    Function to simulate gross margin for a crop phase
    In this function we recalculate revenues for a range of crop prices.
    """

    # get processed data files list
    processed_data_list = getProcessedDataList()

    # Loop through each processed data file
    # loop through to read in
    for file in processed_data_list:
        filepath = os.path.join(get_processed_data_path(), file)
        data = pd.read_csv(filepath)

        ## append dates to data file using year, month and day columns
        data['date'] = pd.to_datetime(data[['year', 'month', 'day']])

        # reset data index
        data.reset_index(drop=True, inplace=True)

        #initialise arrays
        operational_costs_dollars = []
        material_input_costs_dollars = []
        revenue_dollars = []
        gross_margin_dollars = []
        sites_list = []
        plots_list = []
        years_list = []
        crop_sequence_number = []

        # subset by site and plot
        sites = [*set(data['site'])]

        for site in sites:
            subdat_site = data.loc[data['site'] == site,]

            #get plots and subset
            plots = [*set(subdat_site['plotID'])]

            for plot in plots:

                # check if 'BUFFER' is in the plotID
                if 'BUFFER' in plot:
                    # skip this plot
                    continue

                subdat_plot = subdat_site.loc[subdat_site['plotID'] == plot]

                # Order the data by date
                subdat_plot = subdat_plot.sort_values(by=['year', 'month', 'day'])

                subdat_plot = genStateSeriesToMatchProcessedData(subdat_plot)

                # Check if the plot has a crop sequence (i.e. There is a 'CROP' sequence followed by at least one 'FALLOW' state)
                if not (checkExistenceOfCropState(subdat_plot['state'].tolist())):
                    sites_list.append(site)
                    plots_list.append(plot)
                    years_list.append('NA')

                    operational_costs_dollars.append('NA')
                    material_input_costs_dollars.append('NA')
                    revenue_dollars.append('NA')
                    gross_margin_dollars.append('NA')

                    crop_sequence_number.append('NA')
                    continue

                else:
                    # while there is a complete crop sequence left in subdat_plot, calculate gross margin
                    # initialise crop sequence number
                    crop_sequence_ind = 1

                    while checkExistenceOfCropState(subdat_plot['state'].tolist()):
                        # A crop sequence starts from immediately after harvest (i.e. 'FALLOW') state and
                        # ends immediately after to the next harvest
                        # so a crop sequence will look like this in the state variable:
                        # FALLOW, FALLOW, ..., FALLOW, CROP, CROP, ..., CROP, [FALLOW]
                        # Where the last FALLOW is not included in this crop sequence
                        # Also note that ALL plots start in a FALLOW state
                        crop_sequence = getCropSequenceIndex(subdat_plot['state'].tolist())
                        # get final data frame including cost and revenue components
                        subdat_plot_crop = subdat_plot.iloc[0:crop_sequence['crop_end_index']+1] #pandas: start index is inclusive, end index is exclusive

                        # calculate crop gross margin inputs
                        operating_costs = float(np.sum(subdat_plot_crop['costs_activity_dollars']))
                        material_costs = float(np.sum(subdat_plot_crop['costs_product_applied_dollars']))
                        gross_revenue = float(np.sum(subdat_plot_crop['revenue_crops_dollars']))

                        sites_list.append(site)
                        plots_list.append(plot)
                        years_list.append(subdat_plot_crop['year'].iloc[0])

                        operational_costs_dollars.append(operating_costs)
                        material_input_costs_dollars.append(material_costs)
                        revenue_dollars.append(gross_revenue)
                        gross_margin_dollars.append(gross_revenue - operating_costs - material_costs)
                        crop_sequence_number.append(crop_sequence_ind)

                        # remove the crop sequence from the subdat_plot
                        subdat_plot = subdat_plot.iloc[crop_sequence['crop_end_index'] + 1:] #pandas shite - start index is inclusive, end index is exclusive WTF
                        #check if empty
                        if subdat_plot.empty:
                            break
                        crop_sequence_ind += 1

        gm_df = pd.DataFrame({
            'site' : sites_list,
            'plot' : plots_list,
            'year' : years_list,
            'crop_sequence' : crop_sequence_number,
            'operational_costs_dollars' : operational_costs_dollars,
            'material_input_costs_dollars' : material_input_costs_dollars,
            'plot_yield_kilograms_per_hectare' : 'TBD',
            'plot_main_crop' : 'TBD',
            'plot_revenue_dollars' : revenue_dollars,
            'plot_gross_margin_dollars' : gross_margin_dollars
        })

        # write to file with processed file date
        file_path_gm_csv = get_gross_margin_data_path()
        if os.path.exists(file_path_gm_csv):
            gm_df.to_csv(get_gross_margin_data_path(file))
        else:
            os.mkdir(file_path_gm_csv)
            gm_df.to_csv(get_gross_margin_data_path(file))


def getAnnualGrossMargin():

    #get processed_data_files_list
    processed_data_list = getProcessedDataList()

    # loop through to read in
    for file in processed_data_list:
        filepath = os.path.join(get_processed_data_path(), file)
        data = pd.read_csv(filepath)

        #initialise arrays
        annual_plot_operational_costs_dollars = []
        annual_plot_material_input_costs_dollars = []
        annual_plot_revenue_dollars = []
        annual_plot_gross_margin_dollars = []
        sites_list = []
        plots_list = []
        years_list = []

        # subset by site, plot, year and calculate gross margins
        sites = [*set(data['site'])]

        for site in sites:
            subdat_site = data.loc[data['site'] == site,]

            #get plots and subset
            plots = [*set(subdat_site['plotID'])]

            for plot in plots:
                subdat_plot = subdat_site.loc[subdat_site['plotID'] == plot]

                # get years
                years = [*set(subdat_plot['year'])]

                for year in years:
                    subdat_year = subdat_plot.loc[subdat_plot['year'] == year]

                    # get final data frame including cost and revenue components
                    operating_costs = float(np.sum(subdat_year['costs_activity_dollars']))
                    material_costs = float(np.sum(subdat_year['costs_product_applied_dollars']))
                    gross_revenue = float(np.sum(subdat_year['revenue_crops_dollars']))

                    sites_list.append(site)
                    plots_list.append(plot)
                    years_list.append(year)

                    annual_plot_operational_costs_dollars.append(operating_costs)
                    annual_plot_material_input_costs_dollars.append(material_costs)
                    annual_plot_revenue_dollars.append(gross_revenue)
                    annual_plot_gross_margin_dollars.append(gross_revenue - operating_costs - material_costs)

        gm_df = pd.DataFrame({
            'site' : sites_list,
            'plot' : plots_list,
            'year' : years_list,
            'annual_plot_operational_costs_dollars' : annual_plot_operational_costs_dollars,
            'annual_plot_material_input_costs_dollars' : annual_plot_material_input_costs_dollars,
            'annual_plot_revenue_dollars' : annual_plot_revenue_dollars,
            'annual_plot_gross_margin_dollars' : annual_plot_gross_margin_dollars
        })

        # write to file with processed file date
        file_path_gm_csv = get_gross_margin_data_path()
        print(file_path_gm_csv)
        print(file)
        if os.path.exists(file_path_gm_csv):
            gm_df.to_csv(get_gross_margin_data_path(file))
        else:
            os.mkdir(file_path_gm_csv)
            gm_df.to_csv(get_gross_margin_data_path(file))


