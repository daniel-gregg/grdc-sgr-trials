### A schema representation of fields for crop and crop variety registration as a reference dataframe

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from typing_extensions import TypedDict
from pyprojroot.here import here

#Crop names
class Crops(str, Enum):
    wheat = 'wheat'
    barley = 'barley'
    canola = 'canola'
    lentil = 'lentil'
    vetch = 'vetch'
    oat = 'oat'
    fababean = 'fababean'
    fieldpea = 'fieldpea'
    clover = 'clover'
    chicory = 'chicory'
    perennialRyegrass = 'perrenialryegrass'
    subClover = 'subclover'
    millet = 'millet'
    brassica = 'brassica'
    durum = 'durum'
    tillageradish = 'tillageradish'

#Varieties as a dictionary for easier validation
varieties = {
    'wheat':['Scepter', 'BigRed', 'Beauford', 'Calibre', 'Hammer CL', 'Rockstar','Other'],
    'barley': ['Maximus', 'Commondus', 'Planet', 'RGT Planet', 'Compass', 'Titan AX','Other'],
    'canola': ['44Y94 CL', '44Y94', '44Y90', '45Y95', 'Raptor TF', 'PY520TC', 'Enforcer CT', 'Emu TF','Other'],
    'lentil': ['GIA Thunder', 'Hurricane', 'Hurricane XT','Other'],
    'vetch': ['Morava', 'Volga', 'Benatas', 'Timok','Other'],
    'oat': ['Yallara', 'Kingbale','Other'],
    'fababean': ['Bendoc', 'Amberley','Other'],
    'fieldpea': ['Wharton', 'PBA Wharton','Other'],
    'clover' : ['Other',None],
    'chicory' : ['Other',None],
    'perrenialryegrass' : ['Other',None],
    'subclover' : ['Other',None],
    'millet' : ['Other',None],
    'brassica' : ['Other',None],
    'durum' : ['Bittali','Other'],
    'tillageradish' : ['Other',None]
}

#Planting reason - improves detail for pasture and other crops above (can move pasture types into own types)
class Reason(str, Enum):
    cropForSale = 'Crop For Sale'
    fodder = 'Fodder'
    hay = 'Hay'
    silage = 'Silage'
    soilManagement = 'Soil Management'

#Crops and crop varieties
#Whenever a plot-planted crop data point is validated it WILL be added to a plot-date-planted-cropname-harvest dataframe
#This dataframe is then used for validation of harvest observations (i.e. cannot harvest wheat from a barley planted plot)
class PlantedCrops(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    #identifying details
    plotID: str = Field(..., max_length=20)

    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a validator to ensure the date is not in the future
    
    #Crops planted
    crop1Name = Crops
    crop2Name = Crops
    crop3Name = Crops

    #crop variety
    crop1Variety = str
    @field_validator('varietyName')
    @classmethod
    def checkName(cls, varname, crop = crop1Name):
        #define error string
        errorStr = "Variety not found in list, ensure it is one of: " + varieties[crop] + ". If you think it should be please contact administrator to add new variety to list"
        #create check boolean
        checkInVarieties = varname in varieties[crop]
        #return or raise error string
        if checkInVarieties:
            return varname
        else:
            raise errorStr
        
    crop2Variety = str
    @field_validator('varietyName')
    @classmethod
    def checkName(cls, varname, crop = crop2Name):
        #define error string
        errorStr = "Variety not found in list, ensure it is one of: " + varieties[crop] + ". If you think it should be please contact administrator to add new variety to list"
        #create check boolean
        checkInVarieties = varname in varieties[crop]
        #return or raise error string
        if checkInVarieties:
            return varname
        else:
            raise errorStr
        
    crop3Variety = str
    @field_validator('varietyName')
    @classmethod
    def checkName(cls, varname, crop = crop3Name):
        #define error string
        errorStr = "Variety not found in list, ensure it is one of: " + varieties[crop] + ". If you think it should be please contact administrator to add new variety to list"
        #create check boolean
        checkInVarieties = varname in varieties[crop]
        #return or raise error string
        if checkInVarieties:
            return varname
        else:
            raise errorStr

    #Seed treament for crops planted?
    seedTreatment1Bool = bool
    seedTreatment2Bool = bool
    seedTreatment3Bool = bool

    #Planting reason
    reason = Reason

    #Planting density
    crop1SowingDensity = float = Field(..., ge=0,le=500, description="Kg per hectare")
    crop2SowingDensity = float = Field(..., ge=0,le=500, description="Kg per hectare")
    crop3SowingDensity = float = Field(..., ge=0,le=500, description="Kg per hectare")
    
    #Comments are optional
    comments: str = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")
