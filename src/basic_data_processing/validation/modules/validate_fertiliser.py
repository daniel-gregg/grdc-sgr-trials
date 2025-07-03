"""
    Test function for validation program for fertilisers
    These can be used as models for the validators themselves
"""

import pandas as pd
import numpy as np
from pyprojroot.here import here
import sys

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.basic_data_processing.validation.schemas.schema_fertiliser import (
    FertiliserApplicationsModel,
    FertiliserProductsModel
)
from typing import List
from pydantic import ValidationError

from src.utils.base_paths import get_reference_data_path

### Test the fertiliser products model schema
def validateFertiliserProductsModel():

    #Read in referfence data
    fertilisers = pd.read_csv(get_reference_data_path('FertProductData.csv'))

    try: 
        #Convert NA to None type
        fertilisers = fertilisers.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = fertilisers.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FertiliserProductsModel(**record)
        
        #return the df for further processing)
        return(fertilisers)

    except ValidationError as e:
        print(e)


### Test the fertiliser products model schema
# This relies on a validated fertiliser products model 
# which is imported into the 'schema_fertilisers.py' file
def validateFertiliserApplicationsModel(treatments):

    try: 
        #Convert pandas DF to dictionary
        df_dict = treatments.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            try:
                # Validate each record against the FertiliserApplicationsModel schema
                FertiliserApplicationsModel(**record)
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
