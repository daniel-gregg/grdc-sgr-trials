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
from src.sgr_data.validate.modules.validate_pesticide import validatePesticideApplicationsModel
from src.sgr_data.validate.modules.validate_sowing import validateSowingModel
from src.sgr_data.validate.modules.validate_termination import validateTerminationModel


def validateData(data, schema):
    #validate data against schema
    if schema=='fertiliser':
        return validateFertiliserApplicationsModel(data)
    if schema=='fungicide':
        return validateFungicideApplicationsModel(data)
    if schema=='herbicide':
        return validateHerbicideApplicationsModel(data)
    if schema=='pesticide':
        return validatePesticideApplicationsModel(data)
    if schema=='sowing':
        return validateSowingModel(data)
    if schema=='termination':
        return validateTerminationModel(data)

