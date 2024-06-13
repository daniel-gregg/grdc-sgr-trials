"""
    Test function for validation program for sowing data entry
    These can be used as models for the validators themselves
"""


import pandas as pd
import numpy as np
from pyprojroot.here import here
import sys

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.sgr_data.validate.schemas.schema_sowing import (
    SowingModel
)

from src.sgr_data.validate.tests.checkPlotState import checkPlotState

from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def testSowingModel():

    #Read in test data
    sowing_data = pd.read_csv(here('src/sgr_data/data/test_data/testSowingDataPass.csv'))

    #Note empty values in a .csv are read in as 'nan'. 
    #Need to replace these prior to implementing as dict

    try: 
        #Convert NA to None type
        sowing_data = sowing_data.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = sowing_data.to_dict(orient='records')
        
        #Loop through each record and validate against the model
        for record in df_dict:

            #validate types against schema model
            SowingModel(**record)
            
            #If pass, validate against plot state
            checkPlotState(
                plot_id=record.get('plotID'), 
                plotActivityType='FALLOW', 
                crop1=record.get('crop1Name'), 
                crop2=record.get('crop2Name'), 
                crop3=record.get('crop3Name')
                )
        
        # If all pass return the DF
        return(sowing_data)

    except ValidationError as e:
        print(e)


testSowingModel()