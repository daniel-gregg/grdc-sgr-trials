# GRDC SGR data input program: Raw data collation and storage

This short document provides an overview of the directory structure for collation of raw data into .csv files for upload and validation.

This file is located within the ‘src/sgr_data/data/raw_data’ directory and is intended as an overview of the associated processes for that directory. Specifically, this directory is associated with the storage of raw data obtained from trial operations consultants (sites) for further processing, validation and preparation for analysis.

*Note these data have already been put into appropriate template format from the original data recording efforts of trial operations consultants. Those original data will be held in a separate directory with the same base structure (i.e. separated by site and with a clear date structure)*

The process of entering data from receipt of trial operators records to adding data for processing is as follows:

1.  Request data from trial operations consultants on a quarterly basis
2.  Translate data to upload templates provided in this form
3.  Query any gross omissions or mistakes
4.  Save files in the referent site-activity directory within the ‘src/sgr_data/data/raw_data’ directory (e.g. ‘roseworthy/fertiliser/’) with naming convention as:

    ‘DD_MM_YYYY ’  
    for example – ‘01_01_2024’

5.  Notify data manager of new data availability when all data has been incorporated into the relevant folder
6.  Respond to any errors in upload and validation arising from the new data and coordinate their correction

The folder structure and expectations regarding naming conventions is shown in Figure 1 below.

**Figure 1: A depiction of the folder structure holding raw data files for upload and validation**
![raw data directory structure and guidance](../../../../media/raw_data_directory_structure.png)
