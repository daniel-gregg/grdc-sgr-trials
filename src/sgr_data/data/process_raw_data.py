### Uses the upload package to upload new data saved in 'sgr/sgr_data/data/raw_data/'
### Passes new date entries through the relevant validators
### Saves new data to relevant dataframes if validation passes

# base imports
from pyprojroot.here import here
import sys
import os
from copy import deepcopy
from pydantic import ValidationError

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.sgr_data.upload.upload import uploadFiles
from src.sgr_data.validate.validate import validateData

### list sites and activities in the raw_data file


#sites:
sites_list = os.listdir(os.path.join('src' ,'sgr_data', 'data', 'raw_data'))
# remove the 'master' folder from the sites list
sites_list.remove('master')

#activities:
activities_list = os.listdir(os.path.join('src' ,'sgr_data', 'data', 'raw_data', 'master'))
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
                path_to_target = os.path.join('src' ,'sgr_data', 'data', 'raw_data', site, activity)
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
                path_for_saving = os.path.join('src' ,'sgr_data', 'data', 'validated_data', site, activity)
                save_path = os.path.join(path_for_saving, file_name_date) 
                valid_data_frame.to_pickle(save_path)
                print('successfully uploaded file {} for activity {}\n\n'.format(file_name_date, activity) )
        
        else:
            print('no new data to upload\n')
        



