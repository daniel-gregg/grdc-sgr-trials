"""
    Test function for validation program for pesticides
    These can be used as models for the validators themselves
"""


import pandas as pd
import numpy as np
from pyprojroot.here import here
import sys

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.sgr_data.validate.schemas.schema_pests import (
    PestsApplicationsModel,
    PestProductsModel
)
from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def validatePestProductsModel():

    #Read in test data
    pests = pd.read_csv(here('src/sgr_data/data/test_data/testPestProductData.csv'))

    #Note empty values in a .csv are read in as 'nan'. 
    #Need to replace these prior to implementing as dict
    try: 
        #Convert NA to None type
        pests = pests.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = pests.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            PestProductsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(pests)

    except ValidationError as e:
        print(e)


### Test the fertiliser products model schema
# This relies on a validated fertiliser products model 
# which is imported into the 'schema_fertilisers.py' file
def validatePestApplicationsModel():

    #Initialise fake dataframe
    applications = pd.DataFrame(
            [
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "pestProductName": "shoofly", "pestProductUnitsApplied": 'litres', "pestProductValue": 12, "pestProductApplicationTiming": "sowing", "comments": 'Leave your number here'},
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "pestProductName": "Four products", "pestProductUnitsApplied": 'kilograms', "pestProductValue": 12, "pestProductApplicationTiming": None, "comments": 'Leave your number here'},
            ]
        )

    try: 
        #Convert pandas DF to dictionary
        df_dict = applications.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            PestsApplicationsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(applications)

    except ValidationError as e:
        print(e)
