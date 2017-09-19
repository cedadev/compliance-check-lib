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


class NCVariableMetadataCheck(NCFileCheckBase):
    """
    The variable '{var_id}' must exist in the file with the attributes defined in the  
    controlled vocabulary specified.
    """
    short_name = "Variable Metadata: {var_id}"
    defaults = {}
    message_templates = ["Variable '{var_id}' not found in the file so cannot perform other checks.",
                         "Each variable attribute is checked separately."]

    level = "HIGH"

    def _setup(self):
        "Checks that the variable ID (var_id) argument has been provided."
        if "var_id" not in self.kwargs:
            raise ParameterError("Keyword argument for NC Variable Metadata Check must be: 'var_id'.")


    def _check_nc_attribute(self, variable, attr, expected_value):
        """
        Checks that attribute ``attr`` is in the netCDF4 Variable and the value
        matches the expected value. Returns True for success and False for failure.
 
        :param variable: netCDF4 Variable instance.
        :param attr: attribute name (string).
        :param expected_value: value that we expect to find (varied type).
        :return: boolean.
        """
        value = getattr(variable, attr)
        KNOWN_IGNORES = ("<derived from file>",)

        if expected_value in KNOWN_IGNORES:
            return True

        if value == expected_value:
            return True

        return False


    def _get_result(self, primary_arg):
        ds = primary_arg
        var_id = self.kwargs["var_id"]

        # First, work out the overall 'out of' value based on number of attributes
        vocabs = ESSVocabs(*self.vocabulary_ref.split(":")[:2])
        lookup = "variables:{}".format(var_id)
        expected_attr_dict = vocabs.get_value(lookup, "data")

        self.out_of = 1 + len(expected_attr_dict) * 2
        score = 0

        # Check the variable first 
        if var_id not in ds.variables:
            messages = self.get_messages()[:1]
            return Result(self.level, (score, self.out_of),
                          self.get_short_name(), messages)

        score += 1
        variable = ds.variables[var_id]
        messages = []

        # Check the variable attributes one-by-one
        for attr, expected_value in expected_attr_dict.items():
            if attr not in variable.ncattrs():
                messages.append("Required variable attribute '{}' is not present for "
                                "variable: '{}'.".format(attr, var_id))
            else:
                score += 1
                # Check the value of attribute
                check = self._check_nc_attribute(variable, attr, expected_value)
                if check:
                    score += 1
                else:
                    messages.append("Required variable attribute '{}' has incorrect value ('{}') "
                                    "for variable: '{}'. Value should be: '{}'.".format(attr, 
                                    getattr(variable, attr), var_id, expected_value)) 

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)
