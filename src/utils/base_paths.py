## Set all base dir paths here as functions

# base imports
import os

def get_base_data_path():
    return (os.path.join('data'))

def get_raw_data_path(site = None, activity = None):
    if not site:
        return (os.path.join('data', 'raw_data'))
    else:
        if activity:
            return (os.path.join('data', 'raw_data', site, activity))
        else:
            return (os.path.join('data', 'raw_data', site))


def get_validated_data_path(site = None, activity = None):
    if not site:
        return (os.path.join('data', 'validated_data'))
    else:
        if activity:
            return (os.path.join('data', 'validated_data', site, activity))
        else:
            return (os.path.join('data', 'validated_data', site))

def get_reference_data_path(file):
    # type must be one of the files in the reference data folder as a string and including the file extension
    # e.g. 'fertiliser.csv'
    return os.path.join('data', 'reference_data', file)

def get_processed_data_path():
    return os.path.join('data', 'processed_data')

def get_gross_margin_data_path(file = None):
    if not file:
        return os.path.join('data', 'outputs', 'gross_margins')
    else:
        return os.path.join('data', 'outputs', 'gross_margins',file)

def get_outputs_path():
    return os.path.join('data', 'outputs')

def get_system_baseline_comparisons_path(file = None):
    if not file:
        return os.path.join('data', 'outputs', 'system_baseline_comparisons')
    else:
        return os.path.join('data', 'outputs', 'system_baseline_comparisons', file)

def get_invalid_data_path(date = None):
    # returns the path to the invalid data folder for a specific site and activity

    if not date:
        return os.path.join('data', 'invalid_data_errors')
    else:
        return os.path.join('data', 'invalid_data_errors', date)