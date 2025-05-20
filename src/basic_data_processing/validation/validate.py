### Passes new date entries through the relevant validators
### Saves new data to relevant dataframes if validation passes

# base imports
from pyprojroot.here import here
import sys

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

import os
from copy import deepcopy
from pydantic import ValidationError

# module imports
from src.utils.upload import uploadFiles
from src.basic_data_processing.validation.modules.validate_fertiliser import validateFertiliserApplicationsModel
from src.basic_data_processing.validation.modules.validate_fungicide import validateFungicideApplicationsModel
from src.basic_data_processing.validation.modules.validate_herbicide import validateHerbicideApplicationsModel
from src.basic_data_processing.validation.modules.validate_pesticide import validatePesticideApplicationsModel
from src.basic_data_processing.validation.modules.validate_sowing import validateSowingModel
from src.basic_data_processing.validation.modules.validate_termination import validateTerminationModel

from src.utils.base_paths import get_base_data_path
from src.utils.base_paths import get_raw_data_path 
from src.utils.base_paths import get_validated_data_path
from src.utils.base_paths import get_reference_data_path

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


def process_raw_formatted_data():
### list sites and activities in the raw_data file


    #sites:
    sites_list = os.listdir(get_raw_data_path())
    # remove the 'master' folder from the sites list
    sites_list.remove('master')

    #activities:
    activities_list = os.listdir(get_raw_data_path('master'))
    activities_list = [x[:-4] for x in activities_list] #strip '.csv'
    ### Get the data files from upload files
    #Store new data files in a nested dict based on {site: activity}
    #Note that the uploadFiles module has functionality to work out if there is new data present and will sort existing from new records
    activity_template_dict = {key:[] for key in activities_list}
    sites_activities_dict = {key:deepcopy(activity_template_dict) for key in sites_list}


    # Loop through each site and activity, call uploadFiles and store resultant dataframe
    for site in sites_activities_dict:
        for activity in sites_activities_dict[site]:
            sites_activities_dict[site][activity].append(uploadFiles(site,activity))

    ### Loop through the sites_activities_dict and call validation on each item - on pass save to processed_data
    # Note: the object returned by 'uploadFiles' above is a list of data files (possibly empty)
    for site in sites_activities_dict:
        for activity in sites_activities_dict[site]:
            data = sites_activities_dict[site][activity]

            #Attempt validation
            print('\n')
            if data: #if not empty
                for i, file in enumerate(data):
                    #check if there is a file to load
                    path_to_target = get_raw_data_path(site, activity)
                    print('checking activity {} for site {} in path {}'.format(activity, site, path_to_target))
                    if not data[i]:
                        print('activity {} has no new data to upload\n'.format(activity))
                        continue
                    
                    #get file name
                    file_name_date = str(*data[i].keys())

                    #attempt validation
                    try:
                        valid_data_frame = validateData(*file.values(),activity)
                    except ValueError as e:
                        raise e
                    except ValidationError as e:
                        raise e
                    except FileNotFoundError as e:
                        raise e
                    
                    #If validation passes, process data
                    #get key (date) for file
                    path_for_saving = get_validated_data_path(site, activity)

                    #join file name to directory path
                    save_path = os.path.join(path_for_saving, file_name_date) 

                    #save as pickle
                    valid_data_frame.to_pickle(save_path)

                    #log outcome
                    print('successfully uploaded file {} for activity {}\n\n'.format(file_name_date, activity) )
            
            else:
                print('no new data to upload\n')
        
