### A schema representation of fields for crop and crop variety planting by plot

import sys
from pyprojroot.here import here

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.utils.auto_enum import AutoEnum, auto, alias

import pandas as pd
from pydantic import (
    BaseModel,
    Field, 
    ConfigDict, 
    StrictBool,
    field_validator,
    model_validator
) 
from typing import Optional
from typing_extensions import Self

#Planting reason - improves detail for pasture and other crops above (can move pasture types into own types)
class Reason(AutoEnum):
    sale = auto()
    fodder = auto()
    hay = auto()
    silage = auto()
    soilManagement = auto()
    
class TimelinessOptions(AutoEnum):
    on_time = auto()
    early = auto()
    late = auto()

#Crops and crop varieties
#Whenever a plot-planted crop data point is validated it WILL be added to a plot-date-planted-cropname-harvest dataframe
#This dataframe is then used for validation of harvest observations (i.e. cannot harvest wheat from a barley planted plot)
class SowingModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    #identifying details
    plotID: str = Field(..., max_length=20)

    year: int = Field(..., ge=2023, le=2029, description="Year of application event")
    month: int = Field(..., ge=1, le=12, description="Month of application event")
    day: int = Field(..., ge=1, le=31, description="Day of application event")
    # To Do - define a va
    
    #Crops planted
    ##Note: Place a validator here to ensure that the last crop has been terminated
    #(excepting the first entry). This ensures that all plots have a complete record
    #of crop phases. 
    crop1Name : str
    crop2Name : Optional[str]
    crop3Name : Optional[str]

    #crop variety
    crop1Variety : Optional[str]    
    crop2Variety : Optional[str]
    crop3Variety : Optional[str]

    #Seed treament for crops planted?
    seedTreatment1Bool : StrictBool
    seedTreatment2Bool : Optional[StrictBool]
    seedTreatment3Bool : Optional[StrictBool]

    #Planting reason
    sowingReason : Reason

    #Planting density
    crop1SowingDensity : float = Field(..., ge=0,le=500, description="gram per square metre")
    crop2SowingDensity : Optional[float] = Field(..., ge=0,le=500, description="gram per square metre")
    crop3SowingDensity : Optional[float] = Field(..., ge=0,le=500, description="gram per square metre")
    
    #Sowing depth
    crop1SowingDepth : float = Field(..., ge=0,le=100,description="sowing depth in millimetres")
    crop2SowingDepth : Optional[float] = Field(..., ge=0,le=100,description="sowing depth in millimetres")
    crop3SowingDepth : Optional[float] = Field(..., ge=0,le=100,description="sowing depth in millimetres")

    #Time of sowing commentary based on comparison to 'normal' for site - TBD as ENUM
    sowingTimelinessDescription : Optional[TimelinessOptions]

    #Comments are optional
    comments: Optional[str] = Field(..., max_length=4000, description="Comments (maximum 4,000 characters)")

    @model_validator(mode='after')
    def validate_choice(self) -> Self:
        
        #get cropnames
        crops = [self.crop1Name, self.crop2Name, self.crop3Name]

        #get variety names
        varieties = [self.crop1Variety, self.crop2Variety, self.crop3Variety]

        #read in the .csv
        ## Load in the crop and varieties data
        try:
            crops_varieties = pd.read_csv(here('src/sgr_data/data/reference_data/varieties.csv'))
        except:
            #If no actual data available, print warning to terminal
            print("There is no longer a 'varieties.csv' file in the 'src/sgr_data/data/reference_data/' directory. This must be replaced for validation to proceed.")

        #now loop through each crop and check the relevant variety
        for crop in range(3):
            #set core variables
            crop_name = crops[crop]
            variety_name = varieties[crop]

            # check if crop_name is empty and if so move to next if it is crop2 or crop3
            if crop_name == None:     #element is empty (and is allowed to be)
                continue              #move to next loop if empty
            
            #create a lower case version
            crop_name = crop_name.lower()
            variety_name = variety_name.lower()

            #remove whitespace
            crop_name = "".join(crop_name.split())
            variety_name = "".join(variety_name.split())

            #check if crop_name is included in the crops in the datafile
            possible_crop_names = list(crops_varieties.columns)
            #convert to lower
            possible_crop_names = [x.lower() for x in possible_crop_names]
            #remove any white space in crop_name

            if not(crop_name in possible_crop_names):
                raise ValueError("Please check your crop names - one is not included in the allowed crops")                           
            
            #now check varieties
            dataframe_index = possible_crop_names.index(crop_name)
            
            if variety_name in list(crops_varieties.iloc[:,dataframe_index]):
                raise ValueError("Variety must be defined in the 'varieties.csv' table in '.../sgr_data/data'")
        
