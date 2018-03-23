"""
test_nc_var_checks.py
======================

Unit tests for the contents of the checklib.register.nc_var_checks_register module.

"""

from checklib.code.errors import ParameterError
from checklib.register.nc_var_checks_register import *
from netCDF4 import Dataset

# TODO: migrate nc_file_checks to a package.
