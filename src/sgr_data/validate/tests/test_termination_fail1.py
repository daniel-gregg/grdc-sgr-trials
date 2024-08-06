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

from src.sgr_data.validate.schemas.schema_termination import (
    TerminationModel
)

from src.sgr_data.validate.tests.testcheckPlotState import checkPlotState

from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def testTerminationModel():

    #Read in test data
    termination_data = pd.read_csv(here('src/sgr_data/data/test_data/testTerminationDataFail1.csv'))
    
    #Note empty values in a .csv are read in as 'nan'. 
    #Need to replace these prior to implementing as dict

    try: 
        #Convert NA to None type
        termination_data = termination_data.replace(np.nan, None)

        #Convert pandas DF to dictionary
        df_dict = termination_data.to_dict(orient='records')
        
        #Loop through each record and validate against the model
        for record in df_dict:

            #validate types against schema model
            TerminationModel(**record)
            
            #If pass, validate against plot state
            checkPlotState(
                plot_id=record.get('plotID'), 
                plotActivityType='SOWING', 
                crop1=record.get('crop1Name'), 
                crop2=record.get('crop2Name'), 
                crop3=record.get('crop3Name')
                )
        
        # If all pass return the DF
        return(termination_data)

    except ValidationError as e:
        print(e)


testTerminationModel()