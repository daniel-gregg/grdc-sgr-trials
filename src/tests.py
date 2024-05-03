### Calls validation tests and runs those
# Also initiates any needed test dataframes required for testing

# utilities
from pyprojroot.here import here

### Load tests
from sgr_data.validate.test_fert import (
    testFertiliserProductsModel,
    testFertiliserApplicationsModel
    #add more as they are developed here
)

### test Fertiliser Products Model
testProductData = testFertiliserProductsModel()

# save the 'testProductData' file to .csv in sgr_data/output
testProductData.to_csv(here('src/sgr_data/output/testProductData.csv'))

### test fertiliser applications model
testFertiliserApplicationsModel()

