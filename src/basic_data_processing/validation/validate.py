### Passes new date entries through the relevant validators
### Saves new data to relevant dataframes if validation passes

# base imports
from pyprojroot.here import here
import sys
import time

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

import os
from copy import deepcopy
from pydantic import ValidationError
import datetime
import pandas as pd

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
from src.utils.base_paths import get_invalid_data_path

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


def validate_crop_state_activities(site, activities_data, path_for_saving_failed_validation):
    """
    Validate a site's NEW sowing + termination records TOGETHER, in chronological (event-date) order,
    threading plot state through an in-memory table.

    Why: sowing/termination validation depends on the plot's state at the time of each event, and each
    valid event changes that state. Validating sowing and termination in separate batches (or in upload
    order) means an earlier termination can be checked against a later season's sowing, so the data has
    to be loaded one activity/season at a time and re-run. Processing both activities interleaved by
    event date, updating the state as we go, removes that requirement - a single run resolves everything.

    All-or-nothing per site: if ANY new sow/term record is invalid, nothing is committed (no pickles
    written, plotStateData.csv untouched) and an error log is written for the site; fix the offending
    record(s) and re-run.

    Assumes forward loading, i.e. new events are dated at/after the plot's already-committed state.
    """
    from src.basic_data_processing.validation.schemas.schema_sowing import SowingModel
    from src.basic_data_processing.validation.schemas.schema_termination import TerminationModel
    from src.basic_data_processing.validation.modules.checkPlotState import checkPlotState

    #nothing to do if there is no new crop-state data for this site
    if not activities_data.get('sowing') and not activities_data.get('termination'):
        return

    activity_model = {'sowing': SowingModel, 'termination': TerminationModel}

    # 1) build each plot's current state from plotStateData.csv (the latest committed row per plot)
    state_path = get_reference_data_path('plotStateData.csv')
    state_df = pd.read_csv(state_path)
    state_df = state_df.replace({float('nan'): None})
    state_df = state_df.copy()
    state_df['__date'] = pd.to_datetime(state_df['DATE'], format='mixed', dayfirst=True)
    state_df = state_df.sort_values('__date')
    current_state = {}
    for _, r in state_df.iterrows():
        #ascending by date, so the last write for each plot is its latest (current) state
        current_state[r['PLOT_ID']] = {'STATE': r['STATE'], 'CROP1': r['CROP1'], 'CROP2': r['CROP2'], 'CROP3': r['CROP3']}

    # 2) collect all NEW sow/term records as dated events, schema-validating each
    events = []
    errors = []
    for activity in ('sowing', 'termination'):
        files = activities_data.get(activity)
        if not files:
            continue
        for upload_key, df in files.items():
            for record in df.to_dict(orient='records'):
                try:
                    activity_model[activity](**record)
                except ValidationError as e:
                    for err in e.errors():
                        errors.append({'plotID': record.get('plotID'), 'activity': activity, 'uploadFile': upload_key,
                                       'errorLocation': err['loc'], 'errorType': err['type'], 'errorMsg': err['msg']})
                    continue
                events.append({'activity': activity, 'uploadFile': upload_key, 'record': record,
                               'date': datetime.datetime(int(record['year']), int(record['month']), int(record['day']))})

    # 3) chronological order; on a same-date tie process TERMINATION before SOWING (end a crop before the next starts)
    events.sort(key=lambda ev: (ev['date'], 0 if ev['activity'] == 'termination' else 1))

    # 4) walk events in order, threading plot state and collecting new state rows.
    # A plot can only change state once per date, so multiple records for the same plot/activity/date
    # (e.g. repeated termination rows, or same-day grouped entries) collapse to a SINGLE state transition -
    # the first drives it; the rest are kept/pickled but do not re-apply (and don't error as 'already fallow').
    new_state_rows = []
    applied_keys = set()
    for ev in events:
        rec = ev['record']
        plot_id = rec.get('plotID')
        state_key = (plot_id, ev['activity'], ev['date'])
        if state_key in applied_keys:
            continue
        applied_keys.add(state_key)
        plot_state = current_state.get(plot_id)
        try:
            if plot_state is None:
                raise ValueError("There is no entry in the plot state data for " + str(plot_id) + ". Please ensure a starting state is initiated for ALL plots prior to data entry")
            newrow = checkPlotState(
                plot_id=plot_id,
                plotActivityType=('SOWING' if ev['activity'] == 'sowing' else 'TERMINATION'),
                year=rec.get('year'), month=rec.get('month'), day=rec.get('day'),
                crop1=rec.get('crop1Name'), crop2=rec.get('crop2Name'), crop3=rec.get('crop3Name'),
                current_state=plot_state)
        except Exception as e:
            errors.append({'plotID': plot_id, 'activity': ev['activity'], 'uploadFile': ev['uploadFile'],
                           'errorLocation': 'checkPlotState', 'errorType': type(e).__name__, 'errorMsg': str(e)})
            continue
        #success - record the new state row and advance the plot's in-memory state
        new_state_rows.append(newrow)
        if ev['activity'] == 'sowing':
            current_state[plot_id] = {'STATE': 'CROP', 'CROP1': rec.get('crop1Name'), 'CROP2': rec.get('crop2Name'), 'CROP3': rec.get('crop3Name')}
        else:
            current_state[plot_id] = {'STATE': 'FALLOW', 'CROP1': None, 'CROP2': None, 'CROP3': None}

    # 5) all-or-nothing commit
    if errors:
        err_df = pd.DataFrame(errors)
        save_path = os.path.join(path_for_saving_failed_validation, site + '_sowing_termination_errors.csv')
        err_df.to_csv(save_path, index=False)
        print('Crop-state validation for site {} found {} error(s); nothing committed. See {}\n'.format(site, len(errors), save_path))
        return

    #all records valid - append the new state rows and pickle each validated upload file
    if new_state_rows:
        pd.concat(new_state_rows, ignore_index=True).to_csv(state_path, mode='a', header=False, index=False)
    for activity in ('sowing', 'termination'):
        files = activities_data.get(activity)
        if not files:
            continue
        for upload_key, df in files.items():
            save_path = os.path.join(get_validated_data_path(site, activity), upload_key)
            df.to_pickle(save_path)
            print('successfully uploaded file {} for activity {} at site {}\n'.format(upload_key, activity, site))


def process_raw_formatted_data():
### list sites and activities in the raw_data file

    # Get the current date as a string
    current_date = datetime.datetime.today()
    formatted_date = current_date.strftime("%d_%m_%Y")

    # check/create the path for saving failed validation
    path_for_saving_failed_validation = get_invalid_data_path(formatted_date)
    if not os.path.exists(path_for_saving_failed_validation):
        os.makedirs(path_for_saving_failed_validation)
    else:
        #remove all files in the directory
        for file in os.listdir(path_for_saving_failed_validation):
            file_path = os.path.join(path_for_saving_failed_validation, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

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
            sites_activities_dict[site][activity] = uploadFiles(site,activity)

    ### Loop through the sites_activities_dict and call validation on each item - on pass save to processed_data
    # Note: the object returned by 'uploadFiles' above is a list of data files (possibly empty)
    for site in sites_activities_dict:

        # sowing + termination are plot-state dependent and must be validated together, in event-date
        # order, so multiple seasons and/or both activities can be loaded in a single run (all-or-nothing)
        validate_crop_state_activities(site, sites_activities_dict[site], path_for_saving_failed_validation)

        for activity in sites_activities_dict[site]:
            # sowing/termination handled above by validate_crop_state_activities
            if activity in ('sowing', 'termination'):
                continue

            data = sites_activities_dict[site][activity]

            #Attempt validation
            if data: #if not empty
                for i, (key, file) in enumerate(data.items()):
                    #check if there is a file to load
                    path_to_target = get_raw_data_path(site, activity)
                    print('checking activity {} for site {} in path {}'.format(activity, site, path_to_target))

                    #get file name
                    file_name_date = key

                    #attempt validation
                    validation_result = validateData(file,activity)

                    # check if validation failed - if so save to dict
                    if isinstance(validation_result, dict):
                        #If validation fails save error log
                        #get key (date) for file
                        file_name = site + '_' + activity + '_' + file_name_date + '.csv'
                        #join file name to directory path
                        save_path = os.path.join(path_for_saving_failed_validation, file_name)
                        #save errors to csv
                        validation_result['errors'].to_csv(save_path, index=False)
                        #log outcome
                        print('Failed to validate file {}. Error log is located in {}\n\n'.format(file_name_date, path_for_saving_failed_validation) )
                    else:
                        #if validation passes, save the data
                        valid_data_frame = validation_result

                        #If validation passes, process data
                        #get key (date) for file
                        path_for_saving = get_validated_data_path(site, activity)

                        #join file name to directory path
                        save_path = os.path.join(path_for_saving, file_name_date)

                        #save as pickle
                        valid_data_frame.to_pickle(save_path)

                        #log outcome
                        print('successfully uploaded file {} for activity {}\n\n'.format(file_name_date, activity) )

                        #wait half a second to avoid overwriting files
                        time.sleep(0.5)

            else:
                print(f'no new data to upload for site {site}\n')

