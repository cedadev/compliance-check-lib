"""
nc_var_checks_register.py
==========================

A register of checks for NetCDF4 Variables.

"""

import os
from netCDF4 import Dataset

from compliance_checker.base import Result

from .nc_file_checks_register import NCFileCheckBase
from checklib.code import nc_util
from checklib.cvs.ess_vocabs import ESSVocabs
from checklib.code.errors import FileError, ParameterError


# TODO: Turn nc_file_checks_register into a package.