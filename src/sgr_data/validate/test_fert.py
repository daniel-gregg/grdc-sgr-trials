"""
    Test function for validation program for fertilisers
    These can be used as models for the validators themselves
"""

import pandas as pd
from sgr_data.validate.schema_fertilisers import (
    FertilisersApplicationsModel,
    FertilisersProductsModel
)
from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def testFertiliserProductsModel():

    #Initialise fake dataframe
    fertilisers = pd.DataFrame(
            [
                {"name": "BigN", "productType": "pellet", "nitrogen": 23.0, "phosphorous": 12.0, "potassium": 2.0, "calcium": 0.5},
                {"name": "SuperP", "productType": "slow_release", "nitrogen": 20.0, "phosphorous": 32.0, "potassium": 2.0, "calcium": 0.5},
                {"name": "Erua", "productType": "liquid", "nitrogen": 48.0, "phosphorous": 0, "potassium": 0, "calcium": 0.0},
                {"name": "OnlyC", "productType": "pellet", "nitrogen": 0.0, "phosphorous": 0, "potassium": 0, "calcium": 14}
            ]
        )

    try: 
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
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fertiliserName": "BigN", "unitsApplied": 'kilograms', "methodApplied": 'banding', "value": 234, "comments": 'Leave your number here'},
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

