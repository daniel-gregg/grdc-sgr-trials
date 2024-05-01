### A schema representation of all fields in the 'fertilisers' dataframe
## Used for validation of uploaded data

import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
from enum import Enum

# Provides a list of potential application types for fertiliser products
class FertiliserType(str, Enum):
    liquid = 'liquid'
    pellet = 'pellet'
    powder = 'powder'

# Provides a model for entry of new fertiliser products that can be referenced in fertiliser applications
class FertilisersTypesModel(BaseModel):
    name: str = Field(..., max_length=20)
    type: FertiliserType
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
    soilinjection = 'soil injection'

# Provides the core model for entering fertiliser application data
class FertilisersApplicationsModel(BaseModel):
    plotID: str = Field(..., max_length=20)
    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    fertiliserName: FertilisersTypesModel.name
    unitsApplied: FertiliserUnits
    methodApplied: FertiliserApplicationMethod
    value: float = Field(..., ge=0,le=1000, description="Number of litres/kg applied PER HECTARE")
    comments: str = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")

#Validator model - NEEDS WORK
class Validator(BaseModel):
    df_dict: List(FertilisersApplicationsModel)

#Validator function
def ValidateFertiliserApplicationData(data):
    try:
        dict_list = data.to_dict(orient="records")
        Validator(dict_list)
        # Send to outputs
        # XXX TO DO
    except ValidationError as e:
        print(e)





