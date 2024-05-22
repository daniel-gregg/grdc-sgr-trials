### A schema representation of all fields in the 'fertilisers' dataframe
## Used for validation of uploaded data

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from typing_extensions import TypedDict
from pyprojroot.here import here

# Provides a list of potential application types for fertiliser products
class FertiliserType(str, Enum):
    liquid = 'liquid'
    pellet = 'pellet'
    powder = 'powder'
    slowrelease = 'slowrelease'

# Enum of the possible units of measurement of fertiliser
class FertiliserUnits(str, Enum):
    kilograms = 'kilograms'
    litres = 'litres'

# Enum of possible application methods
class FertiliserApplicationMethod(str, Enum):
    foliar = 'foliar'
    banding= 'banding'
    fertigation = 'fertigation'
    broadcast = 'broadcast'
    sidedressing = 'sidedressing'
    soilinjection = 'soil_injection'

# Enum of reasons for fertiliser applications - no longer used.
""" class FertiliserTiming(str, Enum):
    preemergence = 'preemergence'
    sowing = 'sowing'
    midcrop = 'midcrop'
    flowering = 'flowering'
    grainset = 'grainset'
    other = 'other' """

class FertilisersProductsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., max_length=20)
    productType: FertiliserType

    #Define and validate method against options in the 'FertiliserApplicationMethod' model - automated by the 'use_enum_values' arg
    productApplicationMethod: FertiliserApplicationMethod
    
    nDAP: float = Field(..., ge=0, le=100, description="Nitrogen as diammonium phospate percent by weight or volume")
    nMAP: float = Field(..., ge=0, le=100, description="Nitrogen as monoammonium phospate percent by weight or volume")
    nUrea: float = Field(..., ge=0, le=100, description="Nitrogen as urea percent by weight or volume")
    phosphorous: float = Field(..., ge=0, le=100, description="Phosphorous percent by weight or volume")
    potassium: float = Field(..., ge=0, le=100, description="Potassium percent by weight or volume")
    calcium: float = Field(..., ge=0, le=100, description="Calcium percent by weight or volume")

# Provides the core model for entering fertiliser application data
# note: all data entries other than identifying fields (date, ID) and comments must be prefaced by 'fert' to ensure
# aggregation of these data with other activities does not generate duplicated field names. 
class FertilisersApplicationsModel(BaseModel):
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
            fertProducts = pd.read_csv(here('src/sgr_data/output/FertProductData.csv'))
        except:
            fertProducts = pd.read_csv(here('src/sgr_data/output/testFertProductData.csv'))
        
        #check if provided 'fertname' is in the existing products list
        if sum(fertProducts['name'].str.contains(fertname))==0:
            raise ValueError("Fertiliser product must be defined in the 'fertProductData' table in '../output'")
        return fertname
    
    
    #Define and validate units against options in the 'FertiliserUnits' model - automated by the 'use_enum_values' arg
    fertUnitsApplied: FertiliserUnits

    fertValue: float = Field(..., ge=0,le=500, description="Number of litres/kg applied PER HECTARE")
    comments: str = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")






