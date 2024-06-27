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

from src.sgr_data.validate.schemas.schema_pesticide import (
    PesticideApplicationsModel,
    PesticideProductsModel
)

from pydantic import ValidationError

### Test the pesticide products model schema
def validatePesticideProductsModel():

    #Read in test data
    pesticides = pd.read_csv(here('src/sgr_data/data/test_data/testPesticideProductData.csv'))

    #Note empty values in a .csv are read in as 'nan'. 
    #Need to replace these prior to implementing as dict
    try: 
        #Convert NA to None type
        pesticides = pesticides.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = pesticides.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            PesticideProductsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(pesticides)

        #TEMPORARY - save this to csv in outputs
        #fertilisers.to_csv('..//output//fertiliserProducts.csv')

    except ValidationError as e:
        print(e)


### Test the fertiliser products model schema
# This relies on a validated fertiliser products model 
# which is imported into the 'schema_fertilisers.py' file
def validatePesticideApplicationsModel(applications):

    try: 
        #Convert pandas DF to dictionary
        df_dict = applications.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            PesticideApplicationsModel(**record)
        
        #If pass, print the DF 
        #(in actual validator you should return the df for further processing)
        return(applications)

    except ValidationError as e:
        print(e)
