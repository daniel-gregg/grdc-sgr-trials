# sgr_gross_margin

A Python package that provides gross margin calculation functionality for usage in the modelling and analysis components of this project 

## modules included
Three modulese are included in this package:
* A basic gross margin calculation function that accepts input cost and output price vectors and returns a single gross margin value
* An input generation function that generates the input cost vector based on user-specified choices and function defaults
* An output generation function the generates an output cost vector based on user-specified choices and function defaults
* A package that supports simulation of these packages [TBD]

## outputs
* If upload or validation fails a relevant warning is returned
* Else a series of dataframes as follows:
    * plotDetails
    * crops
    * herbicideApplications
    * fertiliserApplications
    * fieldActivities
    * pesticideApplications