### A schema representation of all fields in the 'herbicides' dataframe
## Used for validation of uploaded data

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from typing import Optional
from pyprojroot.here import here

# Defines all used herbicide products
# note that all secondary and onwards active ingredients fields are optional - they should be included
# if present but can be omitted if there are only 1 (or more as relevant) active ingredients.
class HerbicidesProductsModel(BaseModel):
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

# Enum of the possible units of measurement of herbicide
class HerbicidesUnits(str, Enum):
    kilograms = 'kilograms'
    litres = 'litres'

# Enum of possible application methods - no longer used.
""" class HerbicidesApplicationMethod(str, Enum):
    foliar = 'foliar'
    broadcast= 'broadcast'
    shielded = 'shielded' """

# Provides the core model for entering herbicide application data
# note: all data entries other than identifying fields (date, ID) and comments must be prefaced by 'herb' to ensure
# aggregation of these data with other activities does not generate duplicated field names. 
class HerbicidesApplicationsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plotID: str = Field(..., max_length=20)

    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a validator to ensure the date is not in the future

    #Define and validate herbicide name against names in the 'HerbicideProductData' df
    herbName: str
    @field_validator('herbName')
    @classmethod
    def herbicide_product_exists(cls, herbname):

        #read in ProductData.csv
        try:
            herbicideProducts = pd.read_csv(here('src/sgr_data/data/HerbProductData.csv'))
        except:
            
            #check if a testProducts csv is available
            try:
                herbicideProducts = pd.read_csv(here('src/sgr_data/data/test_data/testHerbProductData.csv'))
                print("Note that you have not specified a herbicideProducts dataset so the TEST data is being used")
            
            except: 
                return "no pesticide products data ('HerbicideProductData.csv') exists in expected directory (.../sgr_data/data)"
        
        
        #check if provided 'herbicidename' is in the existing products list
        if sum(herbicideProducts['name'].str.contains(herbname))==0:
            raise ValueError("Herbicide product must be defined in the 'herbicideProductData' table in '.../sgr_data/data'")
        return herbname
    
    
    #Define and validate units against options in the 'FertiliserUnits' model - automated by the 'use_enum_values' arg
    herbUnitsApplied: HerbicidesUnits

    #Define and validate method against options in the 'FertiliserApplicationMethod' model - automated by the 'use_enum_values' arg
    herbValue: float = Field(..., ge=0,le=500, description="Number of litres/kg applied PER HECTARE")
    herbApplicationTiming: Optional[str] = Field(..., min_length=1, max_length=1000, description="Comment on herbicide timing (optional)")
    comments: Optional[str] = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")






