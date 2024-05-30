### A schema representation of fields for crop and crop variety termination by plot

##Note: May want to rename this to include non-termination events such as simulated grazing

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, field_validator, StrictBool
from enum import Enum
from typing import Optional
from typing_extensions import Annotated
from pydantic.functional_validators import AfterValidator

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

class TerminationMethod(str, Enum):
    #Provides a range of termination methods, most prominent of which is harvest
    harvest = 'harvest'
    sprayout = 'sprayout'
    tillage = 'tillage'
    no_termination = None

#Crop termination reason - improves detail for pasture and other crops above (can move pasture types into own types)
class Reason(str, Enum):
    success = 'success'#indicates that planting objectives were substantively achieved
    cropFailedWater = 'Crop failed: soil moisture' #crop failed due to insufficient crop water availability
    cropFailedPests = 'Crop failed: pests' #crop failed due to pests
    cropFailedDisease = 'Crop failed: disease' #crop failed due to disease 
    cropSoilWaterManagement = 'Terminate early: soil moisture' #crop terminated early to maintain soil moisture content for later crops
    cropFailedOther = 'Other crop failure: check comments'

#This model captures the ending state of the plot after a crop is terminated
class terminationState(str, Enum):
    fallowStubble = 'fallow as stubble'                 #Crop stubble left
    fallowBareGround = 'fallow as bare ground'          #Bare ground fallow
    fodder = 'fodder'                                   #Crop treated as fodder
    crop = 'crop'                                       #No mechanical harvesting or other activity
    otherterminationstate = 'Other termination state'   #Other state not included here - include in comments


#Crops and crop varieties
#Whenever a plot-planted crop data point is validated it WILL be added to a plot-date-planted-cropname-harvest dataframe
#This dataframe is then used for validation of harvest observations (i.e. cannot harvest wheat from a barley planted plot)
class HarvestedCrops(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ###identifying details
    plotID: str = Field(..., max_length=20)
    
    #date details
    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a validator to ensure the date is not in the future
    
    #Crops harvested
    crop1Name = Crops
    crop2Name = Optional[Crops]
    crop3Name = Optional[Crops]

    #Termination reason
    reason = Reason

    #Yield
    crop1Yield = float = Field(..., ge=0,le=500, description="Kg per hectare")
    crop2Yield = Optional[float] = Field(..., ge=0,le=500, description="Kg per hectare")
    crop3Yield = Optional[float] = Field(..., ge=0,le=500, description="Kg per hectare")
    
    #Update Termination state - ensures that the plot state changes to one of the termination states
    plotState = terminationState

    #Comments are optional
    comments: str = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")

