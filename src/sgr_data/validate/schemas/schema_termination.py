### A schema representation of fields for crop and crop variety termination by plot

##Note: May want to rename this to include non-termination events such as simulated grazing

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, field_validator, StrictBool
from enum import Enum
from typing import Optional
from typing_extensions import Annotated
from pydantic.functional_validators import AfterValidator

#Create a special case-insensitive enum
class CaseInsensitiveEnum(str, Enum):
    @classmethod
    def _missing_(cls, value: str):
        for member in cls:
            if member.lower() == value.lower():
                return member
        return None

#Crop names
class Crops(CaseInsensitiveEnum):
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

class TerminationMethod(CaseInsensitiveEnum):
    #Provides a range of termination methods, most prominent of which is harvest
    harvest = 'harvest'
    sprayout = 'sprayout'
    tillage = 'tillage'
    no_termination = None

#Crop termination reason - improves detail for pasture and other crops above (can move pasture types into own types)
class Reason(CaseInsensitiveEnum):
    success = 'success'#indicates that planting objectives were substantively achieved
    fail_water = 'fail_water' #crop failed due to insufficient crop water availability
    fail_pests = 'fail_pests' #crop failed due to pests
    fail_disease = 'fail_disease' #crop failed due to disease 
    fail_strategic = 'fail_strategic' #crop terminated early for strategic reasons - provide comments
    fail_other = 'fail_other'

#This model captures the ending state of the plot after a crop is terminated
class terminationState(CaseInsensitiveEnum):
    fallowStubble = 'stubble'                           #Crop stubble left
    fallowBareGround = 'bare'                           #Bare ground fallow
    fodder = 'fodder'                                   #Crop treated as fodder
    crop = 'crop'                                       #No mechanical harvesting or other activity
    otherterminationstate = 'Other'                     #Other state not included here - include in comments


#Crops and crop varieties
#Whenever a plot-planted crop data point is validated it WILL be added to a plot-date-planted-cropname-harvest dataframe
#This dataframe is then used for validation of harvest observations (i.e. cannot harvest wheat from a barley planted plot)
class TerminationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ###identifying details
    plotID: str = Field(..., max_length=20)
    
    #date details
    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a validator to ensure the date is not in the future
    
    #Crops harvested
    crop1Name : Crops
    crop2Name : Optional[Crops]
    crop3Name : Optional[Crops]

    #Termination reason
    harvestReason : Reason

    #Yield
    crop1Yield : float = Field(..., ge=0,le=500, description="Kg per hectare")
    crop2Yield : Optional[float] = Field(..., ge=0,le=500, description="Kg per hectare")
    crop3Yield : Optional[float] = Field(..., ge=0,le=500, description="Kg per hectare")
    
    #Update Termination state - ensures that the plot state changes to one of the termination states
    terminationState : terminationState

    #Comments are optional
    comments: str = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")

