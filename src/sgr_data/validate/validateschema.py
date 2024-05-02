"""
    Validation function for pydantic schemas
    Accepts a pandas DF and returns that ONLY if passing validation
    Validation is defined on the referent schema model
    User must pass in a correctly-defined pandas df that refers to a particular schema model
"""

"""
    This was modified from the post at:
    https://www.inwt-statistics.com/blog/pandas-data-frame-validation-with-pydantic-part-2
    Specifically, the use of 'ModelMetaClass' was removed as deprecated
"""

from pydantic import BaseModel
import pandas as pd
from typing import List

def validate_data_schema(data_schema: BaseModel):
    """This decorator will validate a pandas.DataFrame against the given data_schema."""

    def Inner(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if isinstance(res, pd.DataFrame):
                # check result of the function execution against the data_schema
                df_dict = res.to_dict(orient="records")
                
                # Wrap the data_schema into a helper class for validation
                class ValidationWrap(BaseModel):
                    df_dict: List[data_schema]
                # Do the validation
                _ = ValidationWrap(df_dict=df_dict)
            else:
                raise TypeError("Your Function is not returning an object of type pandas.DataFrame.")

            # return the function result
            return res
        return wrapper
    return Inner

#test the function:

