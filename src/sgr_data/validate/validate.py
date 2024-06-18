### Passes new date entries through the relevant validators
### Saves new data to relevant dataframes if validation passes

# base imports
from pyprojroot.here import here
import sys
import asyncio
import os
import pandas as pd
import csv 

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

# module imports
from src.sgr_data.validate.modules import (
    validate_fertiliser,
    validate_fungicide,
    validate_herbicide,
    validate_insecticide,
    validate_pests,
    validate_sowing,
    validate_termination
)

def validateData(data, schema):
    #validate data against schema
    return data

