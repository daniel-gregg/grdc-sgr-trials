### A schema representation of all fields in the 'fungicides' dataframe
## Used for validation of uploaded data

import sys
from pyprojroot.here import here

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))
from src.utils.auto_enum import AutoEnum, auto, alias

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from typing import Optional


from src.utils.base_paths import get_reference_data_path

# Enum of the possible units of measurement of fungicide
class FungicidesUnits(AutoEnum):
    kilograms = alias('kg', 'kilo', 'kilos')
    litres = alias('l', 'liters')

# Defines all used fungicide products
# note that all secondary and onwards active ingredients fields are optional - they should be included
# if present but can be omitted if there are only 1 (or more as relevant) active ingredients.
class FungicideProductsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., max_length=20)
    unitsKgOrLitres: FungicidesUnits
    price: Optional[float]

# Provides the core model for entering fungicide application data
# note: all data entries other than identifying fields (date, ID) and comments must be prefaced by 'fungicide' to ensure
# aggregation of these data with other activities does not generate duplicated field names. 
class FungicideApplicationsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plotID: str = Field(..., max_length=50)

    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a validator to ensure the date is not in the future

    #Define and validate fungicide name against names in the 'FungicidesProductData' df
    name: str
    @field_validator('name')
    @classmethod
    def fungicide_product_exists(cls, fungname):

        #read in ProductData.csv
        try:
            fungicideProducts = pd.read_csv(get_reference_data_path('FungProductData.csv'), index_col=False)
        except:
            
            #check if a testProducts csv is available
            try:
                fungicideProducts = pd.read_csv(here('data/test_data/testFungProductData.csv'))
                print("Note that you have not specified a FungicideProducts dataset so the TEST data is being used")
            
            except: 
                return "no fungicide products data ('FungicideProductData.csv') exists in expected directory (.../sgr_data/data)"
        
        #check if provided 'fungicidename' is in the existing products list
        if sum(fungicideProducts['name'].str.lower().str.contains(fungname.lower().strip()))==0:
            raise ValueError("Fungicide product must be defined in the 'FungicideProductData' table in '.../sgr_data/data'")
        return fungname
    
    
    #Define and validate units against options in the 'FertiliserUnits' model - automated by the 'use_enum_values' arg
    unitsAppliedKgOrLitres: FungicidesUnits

    #Define and validate method against options in the 'FertiliserApplicationMethod' model - automated by the 'use_enum_values' arg
    appliedAmount: float = Field(..., ge=0,le=4000, description="Number of litres/kg applied PER HECTARE")
    comments: Optional[str] = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")






