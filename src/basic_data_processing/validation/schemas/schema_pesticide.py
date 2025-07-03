### A schema representation of all fields in the 'pestticides' dataframe
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

# Enum of the possible units of measurement of pesticide
class PesticidesUnits(AutoEnum):
    kilograms = alias('kg', 'kilo', 'kilos')
    litres = alias('l', 'liters')

# Defines all used pestticide products
# note that all secondary and onwards active ingredients fields are optional - they should be included
# if present but can be omitted if there are only 1 (or more as relevant) active ingredients.
class PesticideProductsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., max_length=20)
    unitsKgOrLitres: PesticidesUnits
    price: Optional[float]

class TargetPest(AutoEnum):
    not_provided = None
    fall_army_worm = alias('faw')
    locusts = alias('grasshoppers')
    other_insects = alias('insects','other')
    rodents = alias('mice', 'mouse', 'rats')
    red_legged_earth_mites = alias('RLEM')
    slugs_or_snails = alias('slug', 'snail', 'slugs', 'snails')

# Provides the core model for entering pesticide application data
# note: all data entries other than identifying fields (date, ID) and comments must be prefaced by 'pesticide' to ensure
# aggregation of these data with other activities does not generate duplicated field names. 
class PesticideApplicationsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plotID: str = Field(..., max_length=50)

    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a validator to ensure the date is not in the future

    # Target pest
    targetPest: TargetPest

    #Define and validate pesticide name against names in the 'PesticidesProductData' df
    name: str
    @field_validator('name')
    @classmethod
    def pesticide_product_exists(cls, pestname):

        #read in ProductData.csv
        try:
            pesticideProducts = pd.read_csv(get_reference_data_path('PestProductData.csv'), index_col=False)
        except:
            
            #check if a testProducts csv is available
            try:
                pesticideProducts = pd.read_csv(here('data/test_Data/testPesticideProductData.csv'))
                print("Note that you have not specified a pesticideProducts dataset so the TEST data is being used")
            
            except: 
                return "no pesticide products data ('PesticideProductData.csv') exists in expected directory (.../sgr_data/output)"
        
        #check if provided 'pessticidename' is in the existing products list
        if sum(pesticideProducts['name'].str.lower().str.contains(pestname.lower().strip()))==0:
            raise ValueError("Pesticide product must be defined in the 'pesticideProductData' table in '.../sgr_data/data'")
        return pestname
    
    
    #Define and validate units against options in the 'PesticideUnits' model - automated by the 'use_enum_values' arg
    unitsAppliedKgOrLitres: PesticidesUnits

    #Amount of pesticide applied
    appliedAmount: float = Field(..., ge=0,le=500, description="Number of litres/kg applied PER HECTARE")
    
    #optional indications regarding timing and comments
    comments: Optional[str] = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")






