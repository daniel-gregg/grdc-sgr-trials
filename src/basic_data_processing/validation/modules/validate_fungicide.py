"""
    Test function for validation program for fungi
    cides
    These can be used as models for the validators themselves
"""


import pandas as pd
import numpy as np
from pyprojroot.here import here
import sys

from src.utils.base_paths import get_reference_data_path

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.basic_data_processing.validation.schemas.schema_fungicide import (
    FungicideApplicationsModel,
    FungicideProductsModel
)
from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def validateFungicideProductsModel():

    #Read in reference data
    fungicides = pd.read_csv(get_reference_data_path('FungProductData.csv'))

    #Note empty values in a .csv are read in as 'nan'. 
    #Need to replace these prior to implementing as dict
    try: 
        #Convert NA to None type
        fungicides = fungicides.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = fungicides.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FungicideProductsModel(**record)
        
        #return the df for further processing)
        return(fungicides)

    except ValidationError as e:
        print(e)


### Test the fertiliser products model schema
# This relies on a validated fertiliser products model 
# which is imported into the 'schema_fertilisers.py' file
def validateFungicideApplicationsModel(applications):

    try: 
        #Convert pandas DF to dictionary
        df_dict = applications.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FungicideApplicationsModel(**record)
        
        #return the df for further processing)
        return(applications)

    except ValidationError as e:
        print(e)
