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


class NCArrayMatchesVocabTermsCheck(NCFileCheckBase):
    """
    The variable 'var_id' must have values that match those specified
    in the vocabulary collection specified.
    """
    short_name = "Variable '{var_id}' array matches vocabulary: {pyessv_namespace}"
    required_args = ["var_id", "pyessv_namespace"]
    defaults = {}
    message_templates = ["Variable '{var_id}' array does not match vocabulary "
                         "collection: '{pyessv_namespace}'"]
    level = "HIGH"

    def _get_result(self, primary_arg):
        ds = primary_arg
        score = 0
        self.out_of = 1

        vocabs = ESSVocabs(*self.vocabulary_ref.split(":")[:2])
        array = ds[self.kwargs["var_id"]][:]
        result = vocabs.check_array_matches_terms(array, self.kwargs["pyessv_namespace"])

        if result:
            score += 1

        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)

