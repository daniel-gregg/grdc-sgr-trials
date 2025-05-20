### Head function for the main operational scripts/functions of the pipeline

# use this to run the pipeline while it remains as a codebase
# any changes to this or other scripts MUST be undertaken using an approved branch-pull-merge process


### Imports
from src.basic_data_processing.validation.validate import process_raw_formatted_data
from src.basic_data_processing.final_processing.prices_and_costs import integratePricesAndCosts
from src.analysis.gross_margin.grossmargin import getAnnualGrossMargin


# To do:
#from src.basic_data_processing.final_processing.remote_sense_data import integrateRemoteSenseData
#from src.basic_data_processing.final_processing.field_measures import integrateFieldMeasures

##### Data processing and validation

# to do
# pre_process_tor_data_files() - locate this in 'pre-processing'

# 
process_raw_formatted_data()

##### Final processing

# integrate price series
# integrate remote sensed data, e.g. rainfal, temp, etc. (TBD)
# integrate other field measures, e.g. soil moisture (TBD)
# saves .csv files to '.../src/sgr_data/processed_data/*today_date.csv*
integratePricesAndCosts()

# to do
# integrateRemoteSenseData()
# integrateFieldMeasures()

##### Analysis (e.g. gross margins, simulations, etc.)

# calculate and generate reporting for gross margins
getAnnualGrossMargin()

##### Detailed reporting (e.g. formatted reports)
# to do 2025
