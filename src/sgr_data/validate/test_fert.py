"""
    Test function for validation program for fertilisers
"""

import pandas as pd
from validateschema import validate_data_schema
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
                {"name": "JustCalcium", "productType": "pellet", "nitrogen": 0.0, "phosphorous": 0, "potassium": 0, "calcium": 14}
            ]
        )

    try: 
        #should pass
        FertilisersProductsModel(**fertilisers)
    except ValidationError as e:
        print(e)


