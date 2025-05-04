# To Do list from meetings

* Allocating activity costs
    * Currently we use an iterative process that checks whether the last row was the same activity/id/date. If so no activity cost is allocated to that row (as it should be the same). 
    * This has the potential to miss entries that are not sequential in data recording. 
    * While it would be preferable to subset by date/activity/id we cannot currently do that as ALL DATES ARE BASED ON DATA ENTRY AND NOT ON ACTIVITY DATE
    * Once this is fixed we can move to a subsetting approach to ensure activity costs are properly allocated. 
    * We may also want to include a separate 'activity' table that maps product applications to activities in the future - this would allow for multiple product categories (e.g. fertiliser + herbicides) to be applied in the same activity as we cannot currently do that.
* Gross margin modelling program
    * write a function to aggregate plots data and calculate gross margins, returning those against plotID
    * write another function that allows plotting of a GM series
    * write another function that calls the plotting function based on system or system-site responses
    * if time, write another function to conduct a t-test on two gm series
    * if time, write a function to loop through all target combinations to return a matrix of t-test p-values with directional and/or magnitude indicators