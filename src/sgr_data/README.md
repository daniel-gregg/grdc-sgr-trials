# sgr_data

A Python package supporting data uploads, data validation and data organisation for the GRDC-SGR-Trials project. 

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