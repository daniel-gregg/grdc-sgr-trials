### A schema representation of fields for crop and crop variety termination by plot

##Note: May want to rename this to include non-termination events such as simulated grazing

import sys
from pyprojroot.here import here

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.utils.auto_enum import AutoEnum, auto, alias

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

#Crop names
class Crops(AutoEnum):
    wheat = auto()
    barley = auto()
    canola = auto()
    lentil = auto()
    vetch = auto()
    oat = auto()
    fababean = auto()
    fieldpea = auto()
    clover = auto()
    chicory = auto()
    perennialRyegrass = auto()
    subClover = auto()
    millet = auto()
    brassica = auto()
    durum = auto()
    tillageradish = auto()

class TerminationMethod(AutoEnum):
    #Provides a range of termination methods, most prominent of which is harvest
    harvest = auto()
    sprayout = auto()
    tillage = auto()
    no_termination = alias('None','',  'no', 'NA', 'nothing')

#Crop termination reason - improves detail for pasture and other crops above (can move pasture types into own types)
class Reason(AutoEnum):
    success = alias('harvest','good','pass') #indicates that planting objectives were substantively achieved
    fail_water = alias('water','dry','drought') #crop failed due to insufficient crop water availability
    fail_pests = alias('vermin', 'insects', 'mice', 'locusts') #crop failed due to pests
    fail_disease = alias('disease', 'fungus', 'infection', 'rot') #crop failed due to disease 
    fail_strategic = alias('management') #crop terminated early for strategic reasons - provide comments
    fail_other = alias('NA','', 'No reason')

#This model captures the ending state of the plot after a crop is terminated
class terminationState(AutoEnum):
    fallowStubble = alias('stubble', 'no till')                           #Crop stubble left
    fallowBareGround = alias('bare ground', 'tillage', 'till')                           #Bare ground fallow
    fodder = alias('grazing')                                  #Crop treated as fodder
    crop = alias('no harvest', 'crop')                                      #No mechanical harvesting or other activity
    otherterminationstate = alias('NA', '', 'other')                     #Other state not included here - include in comments


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

