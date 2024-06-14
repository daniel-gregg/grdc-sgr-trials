"""
    Test function for validation program for herbicides
    These can be used as models for the validators themselves
"""


import pandas as pd
import numpy as np
from pyprojroot.here import here
import sys

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.sgr_data.validate.schemas.schema_herbicides import (
    HerbicidesApplicationsModel,
    HerbicidesProductsModel
)
from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def testHerbicideProductsModel():

    #Read in test data
    herbicides = pd.read_csv(here('src/sgr_data/data/test_data/testHerbProductData.csv'))

    #Note empty values in a .csv are read in as 'nan'. 
    #Need to replace these prior to implementing as dict
    try: 
        #Convert NA to None type
        herbicides = herbicides.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = herbicides.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            HerbicidesProductsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(herbicides)

        #TEMPORARY - save this to csv in outputs
        #fertilisers.to_csv('..//output//fertiliserProducts.csv')

    except ValidationError as e:
        print(e)


### Test the fertiliser products model schema
# This relies on a validated fertiliser products model 
# which is imported into the 'schema_fertilisers.py' file
def testHerbicidesApplicationsModel():

    #Initialise fake dataframe
    #Note, the creation of the instance IGNORES irrelevant variables. This can help with upload strategies (define a single spreadsheet)
    applications = pd.DataFrame(
            [
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "herbName": "No weeds on me", "herbUnitsApplied": 'l', "herbValue": 12, "herbApplicationTiming": "sowing", "comments": 'Leave your number here'},
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "herbName": "No weeds on me", "herbUnitsApplied": 'kilos', "herbMethodApplied": 'shielded', "herbValue": 12, "herbApplicationTiming": None, "comments": 'Leave your number here'},
            ]
        )

    try: 
        #Convert pandas DF to dictionary
        df_dict = applications.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            HerbicidesApplicationsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(applications)

    except ValidationError as e:
        print(e)


#run the tests
testHerbicideProductsModel()
testHerbicidesApplicationsModel()