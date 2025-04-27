### Head function for the main operational scripts/functions of the pipeline

# use this to run the pipeline while it remains as a codebase
# any changes to this or other scripts MUST be undertaken using an approved branch-pull-merge process


### Imports
from src.sgr_data import process_raw_data
from src.sgr_data import aggregate_data

##### Data processing and validation
process_raw_data()

##### Aggregation and basic reporting (.csv outputs of basic structured, prcoessed, data)

# aggregate data:
#   integrate price series
#   aggregate to plot level with activities across time (each activity in one row)
# saves .csv files to '.../src/sgr_data/processed_data/*today_date.csv*
aggregate_data.aggregateAll()

##### Analysis (e.g. gross margins, simulations, etc.)

# calculate and generate reporting for gross margins
# to do 2025

##### Detailed reporting (e.g. formatted reports)
# to do 2025
