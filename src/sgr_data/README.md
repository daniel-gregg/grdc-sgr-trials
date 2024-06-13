# sgr_data

A Python package supporting data uploads, data validation and data organisation for the GRDC-SGR-Trials project. 

## Data
This directory holds the raw data (in 'data/raw data') for upload (via the 'upload' package) and validation (via the 'validation') package. Processed data that is successfully validated is then copied to data (pandas) files in the 'data/processed_data' directory. This processed data is subject to aggregation and further processing to transform raw data into data frames that can be more readily accessed for analysis. These latter processes are independently developed within each of the 'src/sgr_analysis' directories. 

## modules included
Two modules/packages are included in this package:
* A data upload function providing upload from a .csv file (user provided file path)
* A data validation function that checks for the validity of the uploaded data and returns the pandas dataframe if pass (into 'output' folder)

## outputs
* If upload or validation fails a relevant warning is returned
* Else a series of dataframes as follows:
    * plotDetails
    * crops
    * herbicideApplications
    * fertiliserApplications
    * fieldActivities
    * pesticideApplications
* These are located in the 'output' folder