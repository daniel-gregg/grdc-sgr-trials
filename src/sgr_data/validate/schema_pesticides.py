### A schema representation of all fields in the 'fertilisers' dataframe
## Used for validation of uploaded data

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from typing import Optional
from pyprojroot.here import here

# Defines all used pesticide products
# note that all secondary and onwards active ingredients fields are optional - they should be included
# if present but can be omitted if there are only 1 (or more as relevant) active ingredients.
class PesticidesProductsModel(BaseModel):
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
class PesticidesUnits(str, Enum):
    kilograms = 'kilograms'
    litres = 'litres'

# Enum of possible application methods - no longer used.
""" class PesticidesApplicationMethod(str, Enum):
    foliar = 'foliar'
    broadcast= 'broadcast'
    shielded = 'shielded' """

# Provides the core model for entering pesticide application data
# note: all data entries other than identifying fields (date, ID) and comments must be prefaced by 'pesticide' to ensure
# aggregation of these data with other activities does not generate duplicated field names. 
class PesticidesApplicationsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plotID: str = Field(..., max_length=20)

    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a validator to ensure the date is not in the future

    #Define and validate fertiliser name against names in the 'FertilisersTypesModels' df
    pesticideName: str
    @field_validator('pesticideName')
    @classmethod
    def pesticide_product_exists(cls, pestname):

        #read in ProductData.csv
        try:
            pesticideProducts = pd.read_csv(here('src/sgr_data/output/PesticideProductData.csv'))
        except:
            
            #check if a testProducts csv is available
            try:
                pesticideProducts = pd.read_csv(here('src/sgr_data/output/testPesticideProductData.csv'))
                Warning("Note that you have not specified a pesticideProducts dataset so the TEST data is being used")
            
            except: 
                return "no pesticide products data ('PesticideProductData.csv') exists in expected directory (.../sgr_data/output)"
        
        #check if provided 'herbicidename' is in the existing products list
        if sum(pesticideProducts['name'].str.contains(pestname))==0:
            raise ValueError("Pesticide product must be defined in the 'pesticideProductData' table in '.../sgr_data/output'")
        return pestname
    
    
    #Define and validate units against options in the 'FertiliserUnits' model - automated by the 'use_enum_values' arg
    pesticideUnitsApplied: PesticidesUnits

    #Define and validate method against options in the 'FertiliserApplicationMethod' model - automated by the 'use_enum_values' arg
    pesticideValue: float = Field(..., ge=0,le=500, description="Number of litres/kg applied PER HECTARE")
    pesticideApplicationTiming: Optional[str] = Field(..., min_length=1, max_length=1000, description="Comment on pesticide timing (optional)")
    comments: str = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")






