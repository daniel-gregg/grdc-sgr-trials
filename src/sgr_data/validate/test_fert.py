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

from src.sgr_data.validate.schema_fertilisers import (
    FertilisersApplicationsModel,
    FertilisersProductsModel
)
from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def testFertiliserProductsModel():

    #Read in test data
    fertilisers = pd.read_csv(here('src/sgr_data/output/testFertProductData.csv'))

    try: 
        #Convert NA to None type
        fertilisers = fertilisers.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = fertilisers.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FertilisersProductsModel(**record)
        
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
def testFertiliserApplicationsModel():

    #Initialise fake dataframe
    applications = pd.DataFrame(
            [
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fertName": "BigN", "fertUnitsApplied": 'kilograms', "fertValue": 234, "comments": 'Leave your number here'},
            ]
        )

    try: 
        #Convert pandas DF to dictionary
        df_dict = applications.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FertilisersApplicationsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(applications)

    except ValidationError as e:
        print(e)

#run the tests
testFertiliserProductsModel()
testFertiliserApplicationsModel()