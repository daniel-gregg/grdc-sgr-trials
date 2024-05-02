### A schema representation of all fields in the 'fertilisers' dataframe
## Used for validation of uploaded data

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, validator, field_validator
from enum import Enum
from typing_extensions import TypedDict
from validateschema import validate_data_schema

# Provides a list of potential application types for fertiliser products
class FertiliserType(str, Enum):
    liquid = 'liquid'
    pellet = 'pellet'
    powder = 'powder'
    slowrelease = 'slow_release'

# Provides a model for entry of new fertiliser products that can be referenced in fertiliser applications
class FertilisersProductsModel(TypedDict):
    name: str = Field(..., max_length=20)
    productType: FertiliserType
    nitrogen: float = Field(..., ge=0, le=100, description="Nitrogen percent by weight or volume")
    phosphorous: float = Field(..., ge=0, le=100, description="Phosphorous percent by weight or volume")
    potassium: float = Field(..., ge=0, le=100, description="Potassium percent by weight or volume")
    calcium: float = Field(..., ge=0, le=100, description="Calcium percent by weight or volume")

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

# Provides the core model for entering fertiliser application data
class FertilisersApplicationsModel(TypedDict):
    plotID: str = Field(..., max_length=20)
    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")

    #Define and validate fertiliser name against names in the 'FertilisersTypesModels.name' df
    fertiliserName: str
    @field_validator('fertiliserName')
    @classmethod
    def fert_product_exists(cls, fertname):
        fertnames = set(item.value for item in FertilisersProductsModel.name)
        if not all(map(lambda x: x in fertnames, fertname)):
            raise ValueError("Fertiliser product must be defined in the 'fertiliserTypes' dataframe")
        return fertname
    
    #Define and validate units against options in the 'FertiliserUnits' model - automated by the 'use_enum_values' arg
    unitsApplied: FertiliserUnits

    #Define and validate method against options in the 'FertiliserApplicationMethod' model - automated by the 'use_enum_values' arg
    methodApplied: FertiliserApplicationMethod
    value: float = Field(..., ge=0,le=1000, description="Number of litres/kg applied PER HECTARE")
    comments: str = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")






