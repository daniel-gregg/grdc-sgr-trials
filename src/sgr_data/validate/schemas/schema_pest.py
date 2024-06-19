### A schema representation of all fields in the 'pesticides' dataframe
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

# Defines all used pesticide products
# note that all secondary and onwards active ingredients fields are optional - they should be included
# if present but can be omitted if there are only 1 (or more as relevant) active ingredients.
class PestProductsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., max_length=20)
    activeIngredient1: str = Field(..., min_length=1, max_length=100, description="Primary active ingredient name")
    activeIngredient1Value:float = Field(..., ge=0, le=100, description="Percent by weight or volume of active ingredient for primary active ingredient") 
    activeIngredient2: Optional[str] = Field(..., min_length=1, max_length=100, description="Secondary active ingredient name")
    activeIngredient2Value:Optional[float] = Field(..., ge=0, le=100, description="Percent by weight or volume of active ingredient for secondary active ingredient") 
    activeIngredient3: Optional[str] = Field(..., min_length=1, max_length=100, description="Tertiary active ingredient name")
    activeIngredient3Value:Optional[float] = Field(..., ge=0, le=100, description="Percent by weight or volume of active ingredient for tertiary active ingredient") 
    activeIngredient4: Optional[str] = Field(..., min_length=1, max_length=100, description="Quartenary active ingredient name")
    activeIngredient4Value:Optional[float] = Field(..., ge=0, le=100, description="Percent by weight or volume of active ingredient for quarternary active ingredient") 

# Enum of the possible units of measurement of pesticide
class PesticidesUnits(AutoEnum):
    kilograms = alias('kg', 'kilo', 'kilos')
    litres = alias('l', 'liters')

# Provides the core model for entering pesticide application data
# note: all data entries other than identifying fields (date, ID) and comments must be prefaced by 'pesticide' to ensure
# aggregation of these data with other activities does not generate duplicated field names. 
class PestApplicationsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plotID: str = Field(..., max_length=20)

    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a validator to ensure the date is not in the future

    #Define and validate pesticide name against names in the 'PesticidesProductData' df
    pestProductName: str
    @field_validator('pestProductName')
    @classmethod
    def pesticide_product_exists(cls, pestname):

        #read in ProductData.csv
        try:
            pestProducts = pd.read_csv(here('src/sgr_data/data/PestProductData.csv'))
        except:
            
            #check if a testProducts csv is available
            try:
                pestProducts = pd.read_csv(here('src/sgr_data/data/test_Data/testPestProductData.csv'))
                print("Note that you have not specified a pesticideProducts dataset so the TEST data is being used")
            
            except: 
                return "no pesticide products data ('PestProductData.csv') exists in expected directory (.../sgr_data/output)"
        
        #check if provided 'herbicidename' is in the existing products list
        if sum(pestProducts['name'].str.lower().str.contains(pestname.lower()))==0:
            raise ValueError("Pest product must be defined in the 'PestProductData' table in '.../sgr_data/data'")
        return pestname
    
    
    #Define and validate units against options in the 'FertiliserUnits' model - automated by the 'use_enum_values' arg
    pestProductUnitsApplied: PesticidesUnits

    #Define and validate method against options in the 'FertiliserApplicationMethod' model - automated by the 'use_enum_values' arg
    pestProductValue: float = Field(..., ge=0,le=500, description="Number of litres/kg applied PER HECTARE")
    pestProductApplicationTiming: Optional[str] = Field(..., max_length=1000, description="Comment on pest product application timing (optional)")
    comments: Optional[str] = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")






