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

from src.sgr_data.validate.schemas.schema_fertiliser import (
    FertiliserApplicationsModel,
    FertiliserProductsModel
)
from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def validateFertiliserProductsModel(fertiliserProductData):

    try: 
        #Convert NA to None type
        fertilisers = fertilisers.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = fertilisers.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FertiliserProductsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(fertilisers)

        #TEMPORARY - save this to csv in outputs
        #fertilisers.to_csv('..//output//fertiliserProducts.csv')

    except ValidationError as e:
        print(e)


### Test the fertiliser products model schema
# This relies on a validated fertiliser products model 
# which is imported into the 'schema_fertilisers.py' file
def validateFertiliserApplicationsModel(applications):

    try: 
        #Convert pandas DF to dictionary
        df_dict = applications.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FertiliserApplicationsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(applications)

    except ValidationError as e:
        print(e)
