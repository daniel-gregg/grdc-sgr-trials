# sgr_data

A Python package supporting data uploads, data validation and data organisation for the GRDC-SGR-Trials project. 

## modules included
Four modules/packages are included in this package:
* A data upload function providing upload from a .csv file (user provided file path)
* A data validation function that checks for the validity of the uploaded data
* A data organisation package that then translates the validated data to a set of data frames with individual modules for each dataframe (see below)
* A supplementary data package that provides details of chemical inputs (e.g. percent by weight/volume of different ingredients in products included in the data, labour/machinery/consultant costs in different activities per hectare, etc.). 

## outputs
* If upload or validation fails a relevant warning is returned
* Else a series of dataframes as follows:
    * plotDetails
    * crops
    * herbicideApplications
    * fertiliserApplications
    * fieldActivities
    * pesticideApplications