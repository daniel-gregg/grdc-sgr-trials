# sgr_data/validate

A set of python modules that provide schemas and validation programs for data input related to the GRDC SGR project 

## modules included
A set of modules related to data classes/definitions
* These are named as 'schema_xxx' where 'xxx' is the referent dataframe (e.g. 'fertilisers')
A set of validation functions for each schema
* These take in a pandas dataframe and;
* Pass it through the referent validator, then;
* If the dataframe passes validation the dataframe is returned to 'sgr_data/output'
* Else an error message is returned

## outputs
* If upload or validation fails a relevant warning is returned
* Else a validated dataframe is sent to the 'output' folder