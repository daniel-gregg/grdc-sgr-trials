## Set of functions to reset validated data and setPlotstate to allow for re-processing of all data
import os
import sys
from pyprojroot.here import here
import shutil

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

import pandas as pd

from src.utils.base_paths import get_validated_data_path, get_processed_data_path, get_raw_data_path, get_reference_data_path
from src.basic_data_processing.validation.modules import checkPlotState

def reset_plot_state_reference(site = None):
    """
    Reset the plot state reference data by reading the original plotStateData and replacing the processed data.
    """

    if not site:
        # replace current plotStateData with plotStateDataStarting
        original_file = get_reference_data_path('plotStateDataStarting.csv')
        current_file = get_reference_data_path('plotStateData.csv')
        try:
            shutil.copy(original_file, current_file)
        except FileNotFoundError as e:
            raise e
    
    else:
        # read in current reference plot_state_data as pd
        plot_state_data = pd.read_csv(get_reference_data_path('plotStateDataStarting.csv'))
        starting_data = pd.read_csv(get_reference_data_path('plotStateDataStarting.csv'))

        # 
        # delete all records in plot_state_data for 'site' only
        plot_state_data = plot_state_data[~plot_state_data['PLOT_ID'].str.contains(site.upper())]

        # replace records in plot_state_data with starting_data for 'site' only
        plot_state_data = pd.concat([plot_state_data, starting_data[starting_data['PLOT_ID'].str.contains(site.upper())]])    

        # re-save plot state data
        plot_state_data.to_csv(get_reference_data_path('plotStateData.csv'), index=False)

def remove_validated_plot_state_data(site):
    
    # check if the site has a 'sowing' and 'termination' folder in the validated data
    sowing_path = get_validated_data_path(site, 'sowing')
    termination_path = get_validated_data_path(site, 'termination')

    sowing_files = os.listdir(sowing_path) if os.path.exists(sowing_path) else []
    termination_files = os.listdir(termination_path) if os.path.exists(termination_path) else []

    if len(sowing_files)>0:
        # remove all files in the sowing directory
        for file in sowing_files:
            file_path = os.path.join(sowing_path, file)
            os.remove(file_path)

    if len(termination_files)>0:
        # remove all files in the termination directory
        for file in termination_files:
            file_path = os.path.join(termination_path, file)
            os.remove(file_path)

def reset_plot_state_data(site=None):
    """
    For each site, check validated data for 'sowing' and 'termination' and remove all files in those directories
    """
    if not site:
        sites_list = os.listdir(get_raw_data_path())
        # remove the 'master' folder from the sites list
        sites_list.remove('master')

        for site_name in sites_list:
            remove_validated_plot_state_data(site_name)
        
        # reset all plot state data to the starting reference
        reset_plot_state_reference()
    else:
        # remove the validated data for the site
        remove_validated_plot_state_data(site)
        reset_plot_state_reference(site)