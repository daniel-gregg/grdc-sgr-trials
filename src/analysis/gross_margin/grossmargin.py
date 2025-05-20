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
from src.utils.aggregation_utilities import getProcessedDataList
from src.utils.base_paths import get_gross_margin_data_path


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


    