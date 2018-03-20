"""
nc_coords_checks_register.py
============================

A register of checks for coordinates in NetCDF4 files.

"""

import os
from netCDF4 import Dataset

from compliance_checker.base import Result

from .nc_file_checks_register import NCFileCheckBase
from checklib.code import nc_util
from checklib.cvs.ess_vocabs import ESSVocabs
from checklib.code.errors import FileError, ParameterError


class NCCoordVarHasBoundsCheck(NCFileCheckBase):
    """
    The coordinate variable '{var_id}' must exist in the file with a valid bounds variable.
    """
    short_name = "Coord Var has bounds: {var_id}"
    defaults = {}
    message_templates = ["Variable '{var_id}' not found in the file so cannot perform other checks.",
                         "A valid 'bounds' variable does not exist for variable '{var_id}'."]

    level = "HIGH"

    def _setup(self):
        "Checks that required arguments have been provided."
        required_args = ("var_id",)
        for arg in required_args:
            if arg not in self.kwargs:
                raise ParameterError("Keyword arguments for NC Variable Metadata Check must "
                                     "contain: '{}'.".format(arg))


    def _get_result(self, primary_arg):
        ds = primary_arg
        var_id = self.kwargs["var_id"]

        messages = []
        score = 0

        # Check the variable exists first
        if var_id not in ds.variables:
            messages = self.get_messages()[score]
            return Result(self.level, (score, self.out_of),
                          self.get_short_name(), messages)

        score += 1

        # Now check the "bounds" attribute exists and relates to a separate variable
        variable = ds.variables[var_id]

        if "bounds" in variable.ncattrs() and getattr(variable, "bounds") in ds.variables:
            score += 1
        else:
            messages = [self.get_messages()[score]]

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)

