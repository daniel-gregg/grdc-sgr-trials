# grdc-sgr-trials
A python-based set of packages to facilitate research within the GRDC 'Enterprise choice and sequence strategies that drive sustainable and profitable southern Australian farming systems' project. This repo includes, initially, data upload, data validation and data organisation modules and will grow to include related analysis routines. 

# Included packages
There are four main included packages currently:
* sgr_data - this provides for data upload, validation and organisation functionality
* sgr_gross_margin - providing for calculation of gross margins based on field trial data
* sgr_modelling - a set of modelling routines used to generate key outputs of the project
* sgr_analysis - a set of reporting and analysis routines that provide key user interactions with the other functions in this package

# Usage and development
The current focus is on development of the sgr_data module to provide for data upload functionality. This will then enable generation of gross margin and modelling package modules.

The final objective is to link this set of packages/modules to the 'fastApi' python package that will allow hosting of this resource on a server for access via API calls. 
