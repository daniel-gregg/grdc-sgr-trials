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
from src.utils.base_paths import get_reference_data_path

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
                for error in e.errors():
                    # save validation error to validation record
                    if 'validation_list' in locals():
                        validation_list.append({
                            'plotID' : record['plotID'],
                            'errorLocation' : error['loc'],
                            'errorType' : error['type'],
                            'errorMsg' : error['msg']
                        })
                    else:
                        validation_list = [{
                            'plotID' : record['plotID'],
                            'errorLocation' : error['loc'],
                            'errorType' : error['type'],
                            'errorMsg' : error['msg']
                        }]
        
            try:
                #If pass, validate against plot state
                #try:
                plotState = checkPlotState(
                    plot_id=record.get('plotID'), 
                    plotActivityType='TERMINATION', 
                    year = record.get('year'),
                    month = record.get('month'),
                    day = record.get('day'),
                    crop1=record.get('crop1Name'), 
                    crop2=record.get('crop2Name'), 
                    crop3=record.get('crop3Name')
                    )    

                # initialise/add records for plotState
                if 'plotStateRecords' in locals():
                    plotStateRecords = pd.concat([
                        plotStateRecords,
                        plotState
                        ], 
                        ignore_index = True
                        )
                else:
                    plotStateRecords = plotState

            except Exception as e:
                # save validation error to validation records
                if 'validation_list' in locals():
                    validation_list.append({
                        'plotID' : record['plotID'],
                        'errorLocation' : 'checkPlotState',
                        'errorType' : type(e),
                        'errorMsg' : e
                    })
                else:
                    validation_list = [{
                        'plotID' : record['plotID'],
                        'errorLocation' : 'checkPlotState',
                        'errorType' : type(e),
                        'errorMsg' : e
                    }]
        
        # If all pass return return the df for further processing and update plotStateData.csv
        # If ANY fail, return the validation list and do NOT update plotStateData.csv
        if 'validation_list' in locals():
            # there are validation errors, convert the list to a DataFrame
            validation_df = pd.DataFrame(validation_list)
            print("Validation errors found:")
            return {
                'errors': validation_df,
            }
        else:
            # validation was successful
            # update plotStateData.csv
            plotStateRecords.to_csv(get_reference_data_path('plotStateData.csv'), mode='a', header=False, index = False)
            # return sowing data
            return(termination_data)

    except ValidationError as e:
        print(e)