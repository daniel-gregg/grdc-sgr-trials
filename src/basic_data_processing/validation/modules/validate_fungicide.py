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
def validateFungicideApplicationsModel(treatments):

    try: 
        #Convert pandas DF to dictionary
        df_dict = treatments.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            try:
                # Validate each record against the FungicideApplicationsModel schema
                FungicideApplicationsModel(**record)
            except ValidationError as e:
                # save validation error to validation record
                if 'validation_list' in locals():
                    validation_list.append({
                        'plotID': record['plotID'],
                        'error': str(e)
                    })
                else:
                    validation_list = [{
                        'plotID': record['plotID'],
                        'error': str(e)
                    }]

                print(f"Validation error for record {record}: {e}")
            
        
        #return the df for further processing)
        if 'validation_list' in locals():
            # If there are validation errors, convert the list to a DataFrame
            validation_df = pd.DataFrame(validation_list)
            print("Validation errors found:")
            return {
                'errors': validation_df,
            }
        else:
            return(treatments)

    except ValidationError as e:
        print(e)
