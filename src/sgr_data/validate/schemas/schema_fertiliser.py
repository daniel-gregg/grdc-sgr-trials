### A schema representation of all fields in the 'fertilisers' dataframe
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
from pyprojroot.here import here


# Provides a list of potential application types for fertiliser products
class FertiliserType(AutoEnum):
    liquid = auto()
    pellet = auto()
    powder = auto()
    slowrelease = auto()
    granule = auto()

# Enum of the possible units of measurement of fertiliser
class FertiliserUnits(AutoEnum):
    kilograms = alias('kg', 'kilo', 'kilos')
    litres = alias('l', 'liters')

# Enum of possible application methods
class FertiliserApplicationMethod(AutoEnum):
    foliar = auto()
    banding= auto()
    fertigation = auto()
    broadcast = auto()
    sidedressing = auto()
    soilinjection = auto()

class FertiliserProductsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., max_length=20)
    productType: FertiliserType
    units: FertiliserUnits
    price : float

    #Define and validate method against options in the 'FertiliserApplicationMethod' model - automated by the 'use_enum_values' arg
    nitrogen: float = Field(..., ge=0, le=100, description="Nitrogen as urea percent by weight or volume")
    phosphorous: float = Field(..., ge=0, le=100, description="Phosphorous percent by weight or volume")

# Provides the core model for entering fertiliser application data
# note: all data entries other than identifying fields (date, ID) and comments must be prefaced by 'fert' to ensure
# aggregation of these data with other activities does not generate duplicated field names. 
class FertiliserApplicationsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plotID: str = Field(..., max_length=20)

    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a validator to ensure the date is not in the future

    #Define and validate fertiliser name against names in the 'FertilisersTypesModels' df
    fertName: str
    @field_validator('fertName')
    @classmethod
    def fert_product_exists(cls, fertname):

        #read in ProductData.csv
        try:
            fertProducts = pd.read_csv(here('src/sgr_data/data/reference_data/FertProductData.csv'))
        except:
            #check if a testProducts csv is available
            try:
                fertProducts = pd.read_csv(here('src/sgr_data/data/test_data/testFertProductData.csv'))
                print("Note that you have not specified a fertProducts dataset so the TEST data is being used")
            
            except: 
                return "no fertiliser products data ('FertProductData.csv') exists in expected directory (.../sgr_data/data)"
        
        
        #check if provided 'fertname' is in the existing products list
        if sum(fertProducts['name'].str.lower().str.contains(fertname.lower()))==0:
            raise ValueError("Fertiliser product must be defined in the 'fertProductData' table in '..sgr_data//data'")
        return fertname
    
    
    #Define and validate units against options in the 'FertiliserUnits' model - automated by the 'use_enum_values' arg
    fertUnitsApplied: FertiliserUnits

    fertValue: float = Field(..., ge=0,le=500, description="Number of litres/kg applied PER HECTARE")
    comments: Optional[str] = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")






