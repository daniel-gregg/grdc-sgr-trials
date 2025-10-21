## Calculate profitability ratios and test significant differences for reporting BCAs
# Currently uses Hart data only.

# base imports
from pyprojroot.here import here
import sys
import os
import pandas as pd 
import numpy as np
import datetime

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.utils.base_paths import get_gross_margin_data_path
from src.utils.base_paths import get_reference_data_path

# The function:
#   1. Read in the current gross margin data
#   2. Read in the Systems plot ID mapping.csv data fiel from reference_data
#   3. Filter the data based on the target site (currently 'Hart')
#   4. Create groupings of the data by system type
#   5. Calculate profitability ratios for each plot in each system type
#   6. Compare the profitability ratios between system types using statistical tests
#   7. Return a summary of the results in a dataframe including site groupings and plot IDs
#   8. Identify any sytem types that are significantly more profitable than 'baseline' system types and flag these for reporting

def get_profitability_ratios_by_site(site = "hart"){

    ### Read in data ###

    # Find the latest processed gross margin file
    gross_margin_files = os.listdir(get_gross_margin_data_path())
    latest_file = max(gross_margin_files, key=lambda x: os.path.getctime(os.path.join(get_gross_margin_data_path(), x)))
    
    # read in the gross margin data
    gross_margin_data = pd.read_csv(os.path.join(get_gross_margin_data_path(), latest_file))

    # read in the systems mapping data
    systems_mapping_path = os.path.join(get_reference_data_path(), "Hart system mapping with broader categories and nitrogen strategy inferred.csv")
    systems_data = pd.read_csv(systems_mapping_path)
    
    ### Create systems groupings ###
    # systems are indicated by three variables:
    #    1. System category	
    #    2. Gross system category
    #    3. Nitrogen strategy
    # The latter two are inferred from (1)
    # We will use the latter two only.
    # NOTE: there is a need to work with Matt to generate a proper systems identification ID system with different elements at the same ID location so we can group/sort easily - like the ID we created.

}