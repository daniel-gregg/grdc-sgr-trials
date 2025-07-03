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

from src.basic_data_processing.validation.schemas.schema_termination import (
    TerminationModel
)

from src.basic_data_processing.validation.modules.checkPlotState import checkPlotState

from typing import List
from pydantic import ValidationError

### Test the fertiliser products model schema
def validateTerminationModel(termination_data):

    #Note empty values in a .csv are read in as 'nan'. 
    #Need to replace these prior to implementing as dict

    try: 

        #Convert pandas DF to dictionary
        df_dict = termination_data.to_dict(orient='records')
        
        #Loop through each record and validate against the model
        for record in df_dict:

            try:
                # Validate each record against the PesticideApplicationsModel schema
                TerminationModel(**record)
            except ValidationError as e:
                # save validation error to validation record
                if 'validation_list' in locals():
                    validation_list.append({
                        'plotID': record['plotID'],
                        'error': str(e)
                    })
                else:
                    validation_list = [{
                        'plotID': record['plotID'],
                        'error': str(e)
                    }]

                print(f"Validation error for record {record['plotID']}: {e}")
        
            try:
                #If pass, validate against plot state
                #try:
                checkPlotState(
                    plot_id=record.get('plotID'), 
                    plotActivityType='TERMINATION', 
                    year = record.get('year'),
                    month = record.get('month'),
                    day = record.get('day'),
                    crop1=record.get('crop1Name'), 
                    crop2=record.get('crop2Name'), 
                    crop3=record.get('crop3Name')
                    )       
            except Exception as e:
                # save validation error to validation record
                if 'validation_list' in locals():
                    validation_list.append({
                        'plotID': record['plotID'],
                        'error': str(e)
                    })
                else:
                    validation_list = [{
                        'plotID': record['plotID'],
                        'error': str(e)
                    }]
        
        # If all pass return the DF
        #return the df for further processing)
        if 'validation_list' in locals():
            # there are validation errors, convert the list to a DataFrame
            validation_df = pd.DataFrame(validation_list)
            print("Validation errors found:")
            return {
                'errors': validation_df,
            }
        else:
            return(termination_data)

    except ValidationError as e:
        print(e)