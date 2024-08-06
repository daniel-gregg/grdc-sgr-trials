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

from src.sgr_data.validate.schemas.schema_herbicide import (
    HerbicideApplicationsModel,
    HerbicideProductsModel
)
from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def validateHerbicideProductsModel():

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
            HerbicideProductsModel(**record)
        
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
def validateHerbicideApplicationsModel(applications):

    try: 
        #Convert pandas DF to dictionary
        applications.replace(np.nan, "fuck")
        df_dict = applications.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            HerbicideApplicationsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(applications)

    except ValidationError as e:
        print(e)
