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
#df should be a pandas DataFrame with columns (in order):
#   name: str
#   productType: enum (str)
#   nitrogen: int
#   phosphorous: int
#   potassium: int
#   calcium: int
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


### TEST - REMOVE ONCE CONFIRMED WORKING
""" fertilisers = pd.DataFrame(
            [
                {"name": "BigN", "productType": "pellet", "nitrogen": 23.0, "phosphorous": 12.0, "potassium": 2.0, "calcium": 0.5, "price_per_unit":2},
                {"name": "SuperP", "productType": "slow_release", "nitrogen": 20.0, "phosphorous": 32.0, "potassium": 2.0, "calcium": 0.5, "price_per_unit":2},
                {"name": "Erua", "productType": "liquid", "nitrogen": 48.0, "phosphorous": 0, "potassium": 0, "calcium": 0.0, "price_per_unit":2},
                {"name": "OnlyC", "productType": "pellet", "nitrogen": 0.0, "phosphorous": 0, "potassium": 0, "calcium": 14, "price_per_unit":2}
            ]
        )

addFertiliserProductRecords(fertilisers)

applications = pd.DataFrame(
            [
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fertiliserName": "BigN", "unitsApplied": 'kilograms', "methodApplied": 'banding', "value": 234, "comments": 'Leave your number here'},
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fertiliserName": "BigN", "unitsApplied": 'kilograms', "methodApplied": 'banding', "value": 234, "comments": 'Leave your number here'},
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fertiliserName": "BigN", "unitsApplied": 'kilograms', "methodApplied": 'banding', "value": 234, "comments": 'Leave your number here'},
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fertiliserName": "BigN", "unitsApplied": 'kilograms', "methodApplied": 'banding', "value": 234, "comments": 'Leave your number here'},
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fertiliserName": "BigN", "unitsApplied": 'kilograms', "methodApplied": 'banding', "value": 234, "comments": 'Leave your number here'},
                {"plotID": "RS29_P1234", "year": 2024, "month": 3, "day": 23, "fertiliserName": "BigN", "unitsApplied": 'kilograms', "methodApplied": 'banding', "value": 234, "comments": 'Leave your number here'}
            ]
        )

addFertiliserApplicationsRecords(applications)

 """