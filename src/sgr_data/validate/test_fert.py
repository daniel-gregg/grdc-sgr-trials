"""
    Test function for validation program for fertilisers
"""

import pandas as pd
from schema_fertilisers import (
    FertiliserApplicationMethod,
    FertilisersApplicationsModel,
    FertilisersProductsModel,
    FertiliserUnits,
    FertiliserType
)
from typing import List
from pydantic import ValidationError

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
        print(fertilisers)

    except ValidationError as e:
        print(e)

testFertiliserProductsModel()


