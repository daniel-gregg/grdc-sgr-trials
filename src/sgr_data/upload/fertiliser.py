### Holds fertiliser data input functions for calling

# base imports
from pyprojroot.here import here
import sys
import asyncio
import pandas as pd
from pydantic import ValidationError

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

# module imports
from src.sgr_data.validate.schema_fertilisers import (
    FertilisersApplicationsModel,
    FertilisersProductsModel
)

# utilities
async def getCSV(filePath):
    df_ = pd.read_csv(filePath)
    return df_

### Add a fertiliser product to the fertiliserProductsData.csv table
def addFertiliserProductRecords(df):

    try: 
        #Convert pandas DF to dictionary
        df_dict = df.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FertilisersProductsModel(**record)
        
        try:
            #If pass, check if a current fertProducts table exists
            #Note need to use async/await here
            fertProducts = asyncio.run(getCSV(here('src/sgr_data/output/fertProductData.csv')))

            # If it does, append the validated df to the existing fertProducts table and re-write to file
            fertProducts_new = pd.concat([fertProducts,df], ignore_index=True)
            fertProducts_new.to_csv(here('src/sgr_data/output/fertProductData.csv'), mode='w+', index=False)

            #and return df to user
            return(df)
        
        except:
            #If passed but no existing table, create the first entries by writing to file
            df.to_csv(here('src/sgr_data/output/fertProductData.csv'), index=False)

            #and return df to user
            return(df)

    except ValidationError as e:
        print(e)


### Add a fertiliser application entry
# df should be a pandas DataFrame
# See ../validate/schema_fertilisers.py for more information
def addFertiliserApplicationsRecords(df):

    try: 
        #Convert pandas DF to dictionary
        df_dict = df.to_dict(orient='records')
        
        #Loop through each record and validate
        for record in df_dict:
            FertilisersApplicationsModel(**record)

        try:
            #If pass, check if a current fertProducts table exists
            fertRecords = asyncio.run(getCSV(here('src/sgr_data/output/fertiliserApplicationRecords.csv')))
            
            # If it does, append the validated df to the existing fertProducts table and re-write to file
            fertRecords_new = pd.concat([fertRecords,df], ignore_index=True)
            fertRecords_new.to_csv(here('src/sgr_data/output/fertiliserApplicationRecords.csv'), index=False)

            #and return df to user
            return(fertRecords_new)
        
        except:
            #If passed but no existing table, create the first entries by writing to file
            df.to_csv(here('src/sgr_data/output/fertiliserApplicationRecords.csv'), index=False)
            
            #and return df to user
            return(df)

    except ValidationError as e:
        print(e)

