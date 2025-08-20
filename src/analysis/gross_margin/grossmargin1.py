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

from src.utils.base_paths import get_processed_data_path, get_reference_data_path
from src.utils.aggregation_utilities import getProcessedDataList
from src.utils.base_paths import get_gross_margin_data_path

## In order to calculate gross margins at the crop level we need to
# split the data by site, plot and year, then additionally split it by
# crop-sequence. The latter is defined as the period from post harvest to harvest (inclusive)
# one way to do this is to copy the processed_data file then:
# 1. subset by site and plot
# 2. Check that it has a crop sequence (i.e. a sowing and harvest date)
# 3. if yes, then subset by the crop sequence period
# 3. calculate the gross margin for that period
# 4. then remove that data from the copied file
# 5. repeat until no complete crop sequences are left

def getStateChangeIndex(series):
    """
    Function to get the index of sequential states
    This is used to identify the entirety of a state (i.e. FALLOW or CROP).
    """
    for i in range(1, len(series)):
        if series[i] != series[i - 1]:
            return i-1
    return None  # No state change found

def getCropSequenceIndex(dat):
    # returns the index of the first crop sequence in the supplied data
    # dat MUST start with a FALLOW state

    if dat['state'].iloc[0] != 'FALLOW':
        raise ValueError("Data must start with a FALLOW state")

    # Get states first
    states = dat['state'].tolist()

    ### find the index of the first FALLOW state after a CROP state
    # First get the initial sequence of FALLOW states
    fallow_index = getStateChangeIndex(states)
    if fallow_index is None:
        raise ValueError("No FALLOW state found in the data")
    # Now find the index of the first CROP state after the initial FALLOW states
    crop_index = getStateChangeIndex(states[fallow_index:])
    if crop_index is None:
        raise ValueError("No CROP state found in the data")

    # Adjust the crop index to account for the offset
    crop_index += fallow_index

    return ({
        'fallow_end_index' : fallow_index,
        'crop_start_index' : fallow_index + 1,
        'crop_end_index': crop_index
    })

def genStateSeriesToMatchProcessedData(dat):
    """
    Function to generate a state series that matches the processed data.
    plotStateData only records state at change of state date
    processed_data has many entries based on the date of an activity (not necessarily a state change)
    We need a series of state that is 'filled in' to match the processed data
    """

    # note that this ONLY works for a data file with a single plot
    if len(dat['plotID'].unique()) > 1:
        raise ValueError("Data must contain only one plot")

    # Get the plot state data
    plot_state_data = pd.read_csv(get_reference_data_path('PlotStateData.csv'))
    plot_state_data = plot_state_data[['PLOT_ID', 'DATE', 'STATE']]
    plot_state_data['DATE'] = pd.to_datetime(plot_state_data['DATE'], format = 'mixed')

    # subset plot_state_data to match the plotID in dat
    plot_state_data = plot_state_data[plot_state_data['PLOT_ID'] == dat['plotID'].iloc[0]]

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

def getCropSequenceGrossMargin():
    """
    Function to calculate gross margin for a crop sequence.
    This function is a placeholder and needs to be implemented.
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
                subdat_plot = subdat_site.loc[subdat_site['plotID'] == plot]

                # Order the data by date
                subdat_plot = subdat_plot.sort_values(by=['year', 'month', 'day'])

                subdat_plot = genStateSeriesToMatchProcessedData(subdat_plot)

                # Check if the plot has a crop sequence (i.e. at least one of each of 'FALLOW' and 'CROP')
                if not (('FALLOW' in subdat_plot['state'].values) and ('CROP' in subdat_plot['state'].values)):
                    sites_list.append(site)
                    plots_list.append(plot)
                    years_list.append('NA')

                    operational_costs_dollars.append('NA')
                    material_input_costs_dollars.append('NA')
                    revenue_dollars.append('NA')
                    gross_margin_dollars.append('NA')

                else:
                    # while there is a complete crop sequence left in subdat_plot, calculate gross margin
                    # initialise crop sequence number
                    crop_sequence_ind = 1

                    while (('FALLOW' in subdat_plot['state'].values) and ('CROP' in subdat_plot['state'].values)):
                        # A crop sequence starts from immediately after harvest (i.e. 'FALLOW') state and
                        # ends immediately after to the next harvest
                        # so a crop sequence will look like this in the state variable:
                        # FALLOW, FALLOW, ..., FALLOW, CROP, CROP, ..., CROP, [FALLOW]
                        # Where the last FALLOW is not included in this crop sequence
                        # Also note that ALL plots start in a FALLOW state
                        crop_sequence = getCropSequenceIndex(subdat_plot)
                        # get final data frame including cost and revenue components
                        subdat_plot_crop = subdat_plot.iloc[0:crop_sequence['crop_end_index']]

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
                        subdat_plot = subdat_plot.iloc[crop_sequence['crop_end_index'] + 1:]
                        crop_sequence_ind += 1

        gm_df = pd.DataFrame({
            'site' : sites_list,
            'plot' : plots_list,
            'year' : years_list,
            'crop_sequence' : crop_sequence_number,
            'operational_costs_dollars' : operational_costs_dollars,
            'material_input_costs_dollars' : material_input_costs_dollars,
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


