### A schema representation of fields for crop and crop variety termination by plot

##Note: May want to rename this to include non-termination events such as simulated grazing

import sys
from pyprojroot.here import here

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.utils.auto_enum import AutoEnum, auto, alias

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
from typing_extensions import Self

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
    fallowBareGround = alias('bare ground', 'tillage', 'till', 'bare')                           #Bare ground fallow
    fodder = alias('grazing')                                  #Crop treated as fodder
    asis = alias('no harvest')                                      #No mechanical harvesting or other activity
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
    crop1Harvest : str
    crop2Harvest : Optional[str]
    crop3Harvest : Optional[str]

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

    @model_validator(mode='after')
    def validate_choice(self) -> Self:
        
        #get cropnames
        crops = [self.crop1Harvest, self.crop2Harvest, self.crop3Harvest]

        #read in the .csv
        ## Load in the crop and varieties data
        try:
            crops_varieties = pd.read_csv(here('src/sgr_data/data/reference_data/varieties.csv'))
        except:
            #If no actual data available, print warning to terminal
            print("There is no longer a 'varieties.csv' file in the 'src/sgr_data/data/reference_data/' directory. This must be replaced for validation to proceed.")

        #now loop through each crop and check the relevant variety
        for crop_ in range(3):
            #set core variables
            crop_name = crops[crop_]

            # check if crop_name is empty and if so move to next if it is crop2 or crop3
            if crop_name == None:     #element is empty (and is allowed to be)
                continue              #move to next loop if empty
            
            #create a lower case version
            crop_name = crop_name.lower()

            #remove whitespace
            crop_name = "".join(crop_name.split())

            #check if crop_name is included in the crops in the datafile
            possible_crop_names = list(crops_varieties.columns)
            #convert to lower
            possible_crop_names = [x.lower() for x in possible_crop_names]
            #remove any white space in crop_name

            if not(crop_name in possible_crop_names):
                raise ValueError("Please check your crop names - one is not included in the allowed crops")                           
            
