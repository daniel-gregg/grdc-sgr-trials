'''
    A module to calculate/simulate gross margins for a farm enterprise
    Users can:
        * Use default data (TBD) to generate gross margin simulations for selected enterprises/regions (currently just cropping)
        * Specify data to be used including prices, input quantities, output/yield levels and regions
        * Choose to obtain a single estimate or to simulate a chosen number of draws to obtain a distribution of GM outcomes
    The module returns:
        * A Gross margin estimate or vector of estimates
'''

'Python imports'
import numpy as np
import pandas as pd

'Custom imports'
'TBD - this is for addit'


def total_revenue (outputs,output_prices):
    'Check if output and prices vectors are same length'
    if(len(outputs) != len(output_prices)) : 
        return Warning("Outputs and prices output vectors are different lengths")

    'Calculate total revenue as inner product'
    totalRevenue = np.inner(outputs,output_prices)

    'Return totalRevenue'
    return totalRevenue

def total_costs (inputs,input_prices):
    'Check if input and input prices vectors are same length'
    if(len(inputs) != len(input_prices)) : 
        return Warning("Inputs and input prices vectors are different lengths")
    
    'Calculate total cost as inner product'
    totalCost = np.inner(inputs,input_prices)

    'Return totalCost'
    return totalCost

def calculateGrossMargin(user_outputs,user_inputs,S):


    outputs = getOutputs(user_outputs,S)
    output_prices = getOutputPrices(user_outputs,S)
    inputs = getInputs(user_inputs,S)
    input_prices = getInputPrices(user_inputs,S)

    if(S==1):
        R = totalRevenue(outputs,output_prices)
        C = totalCost(inputs,input_prices)
        GM = R - C

    if(S > 1): 
        'loop through to simulate GM distributions'


    return GM

    