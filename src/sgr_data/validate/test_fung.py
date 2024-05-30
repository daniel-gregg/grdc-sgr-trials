"""
    Test function for validation program for fungi
    cides
    These can be used as models for the validators themselves
"""


import pandas as pd
import numpy as np
from pyprojroot.here import here
import sys

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.sgr_data.validate.schema_fungicides import (
    FungicidesApplicationsModel,
    FungicidesProductsModel
)
from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def testFungicideProductsModel():

    #Read in test data
    fungicides = pd.read_csv(here('src/sgr_data/data/test_data/testFungProductData.csv'))

    #Note empty values in a .csv are read in as 'nan'. 
    #Need to replace these prior to implementing as dict
    try: 
        #Convert NA to None type
        fungicides = fungicides.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = fungicides.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FungicidesProductsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(fungicides)

        #TEMPORARY - save this to csv in outputs
        #fertilisers.to_csv('..//output//fertiliserProducts.csv')

    except ValidationError as e:
        print(e)


### Test the fertiliser products model schema
# This relies on a validated fertiliser products model 
# which is imported into the 'schema_fertilisers.py' file
def testFungicidesApplicationsModel():

    #Initialise fake dataframe
    #Note, the creation of the instance IGNORES irrelevant variables. This can help with upload strategies (define a single spreadsheet)
    applications = pd.DataFrame(
            [
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fungicideName": "No weeds on me", "fungicideUnitsApplied": 'litres', "fungicideValue": 12, "fungicideApplicationTiming": "sowing", "comments": 'Leave your number here'},
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fungicideName": "No weeds on me", "fungicideUnitsApplied": 'kilograms', "fungicideMethodApplied": 'shielded', "fungicideValue": 12, "fungicideApplicationTiming": None, "comments": 'Leave your number here'},
            ]
        )

    try: 
        #Convert pandas DF to dictionary
        df_dict = applications.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FungicidesApplicationsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(applications)

    except ValidationError as e:
        print(e)


#run the tests
testFungicideProductsModel()
testFungicidesApplicationsModel()