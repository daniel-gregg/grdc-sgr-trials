### Passes new date entries through the relevant validators
### Saves new data to relevant dataframes if validation passes

# base imports
from pyprojroot.here import here
import sys

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

# module imports
from src.sgr_data.validate.modules.validate_fertiliser import validateFertiliserApplicationsModel
from src.sgr_data.validate.modules.validate_fungicide import validateFungicideApplicationsModel
from src.sgr_data.validate.modules.validate_herbicide import validateHerbicideApplicationsModel
from src.sgr_data.validate.modules.validate_insecticide import validateInsecticideApplicationsModel
from src.sgr_data.validate.modules.validate_pest import validatePestApplicationsModel
from src.sgr_data.validate.modules.validate_sowing import validateSowingModel
from src.sgr_data.validate.modules.validate_termination import validateTerminationModel


def validateData(data, schema):
    #validate data against schema
    if schema=='fertiliser':
        validated = validateFertiliserApplicationsModel(data)
    if schema=='fungicide':
        validated = validateFungicideApplicationsModel(data)
    if schema=='herbicide':
        validated = validateHerbicideApplicationsModel(data)
    if schema=='insecticide':
        validated = validateInsecticideApplicationsModel(data)
    if schema=='pest':
        validated = validatePestApplicationsModel(data)
    if schema=='sowing':
        validated = validateSowingModel(data)
    if schema=='termination':
        validated = validateTerminationModel(data)
    return validated

