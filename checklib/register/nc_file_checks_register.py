"""
nc_file_checks_register.py
==========================

A register of checks for NetCDF4 files.

"""

import os
from netCDF4 import Dataset

from compliance_checker.base import Result

from .callable_check_base import CallableCheckBase
from checklib.code import nc_util
from checklib.cvs.ess_vocabs import ESSVocabs


class NCFileCheckBase(CallableCheckBase):
    "Base class for all NetCDF4 File Checks (that work on a file path."

    def _check_primary_arg(self, primary_arg):
        if not isinstance(primary_arg, Dataset):
            raise Exception("Object for testing is not a netCDF4 Dataset: {}".format(str(primary_arg)))


class GlobalAttrRegexCheck(NCFileCheckBase):
    """
    The global attribute '{attribute}' must exist and have a valid format matching regular expression: ('{regex}').
    """
    short_name = "Global attribute: {attribute}"
    defaults = {}
    message_templates = ["Required '{attribute}' global attribute is not present.",
                         "Required '{attribute}' global attribute value is invalid."]
    level = "HIGH"

    def _setup(self):
        "Checks that both args are provided and fixes double-escape in regex string"
        if "attribute" not in self.kwargs or "regex" not in self.kwargs:
            raise Exception("Keyword arguments for Global Attribute Regex Check must include ('attribute', 'regex').")

        self.kwargs["regex"] = self.kwargs["regex"].replace("\\\\", "\\")

    def _get_result(self, primary_arg):
        ds = primary_arg

        score = nc_util.check_global_attr_against_regex(ds, self.kwargs["attribute"], self.kwargs["regex"])
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class GlobalAttrVocabCheck(NCFileCheckBase):
    """
    The global attribute '{attribute}' must exist and have a valid value from the relevant vocabulary.
    """
    short_name = "Global attribute: {attribute}"
    defaults = {"vocab_lookup": "canonical_name"}
    message_templates = ["Required '{attribute}' global attribute is not present.",
                         "Required '{attribute}' global attribute value is invalid."]
    level = "HIGH"

    def _setup(self):
        "Checks that required args are provided"
        if "attribute" not in self.kwargs:
            raise Exception("Keyword arguments for Global Attribute Vocab Check must include ('attribute').")


    def _get_result(self, primary_arg):
        ds = primary_arg
        vocabs = ESSVocabs(*self.vocabulary_ref.split(":")[:2])

        score = vocabs.check_global_attribute(ds, self.kwargs["attribute"], property=self.kwargs["vocab_lookup"])
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class OneMainVariablePerFileCheck(NCFileCheckBase):
    """
    Only 1 main variable must be written to each NetCDF file (except ancillary and coordinate
    variables that are required to understand the main variable).
    """
    short_name = "One main variable only"
    defaults = {}
    message_templates = ["More than 1 main variable found in the file. Only 1 main variable should be there."]
    level = "HIGH"

    def _get_result(self, primary_arg):
        ds = primary_arg

        success = nc_util.is_there_only_one_main_variable(ds)
        messages = []

        if success:
            score = self.out_of
        else:
            score = 0
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class ValidGlobalAttrsMatchFileNameCheck(NCFileCheckBase):
    """
    All components in the file name must be set as global attributes in the NetCDF file and must be valid
    terms in the relevant controlled vocabulary.
    """
    short_name = "Global attributes match file name/vocab"
    defaults = {"delimiter": "_", "extension": ".nc"}
    message_templates = ["File name does not match global attributes.",
                         "Each global attribute is checked separately."]
    level = "HIGH"

    def _setup(self):
        """
        Uses the instructions given about the order of the file name components to work out
        the 'out of' value for the result.
        """
        not_found = []
        for key in ("delimiter", "extension", "order"):
            if key not in self.kwargs:
                not_found.append(key)

        if not_found:
            raise Exception("Keyword arguments for Global Attribute Regex Check must include: {}.".format(not_found))

        self.kwargs["order"] = self.kwargs["order"].split(",")
        self.out_of = len(self.kwargs["order"]) * 2 + 1

    def _get_result(self, primary_arg):
        ds = primary_arg

        score = 0
        messages = []

        vocabs = ESSVocabs(*self.vocabulary_ref.split(":")[:2])
        fname = os.path.basename(ds.filepath())
        cv_match = vocabs.check_file_name(fname, keys=self.kwargs["order"],
                                          delimiter=self.kwargs["delimiter"],
                                          extension=self.kwargs["extension"])

        if cv_match:
            score += 1
        else:
            messages.append(self.get_messages()[0])

        # Check global attributes one-by-one
        for attr in self.kwargs["order"]:
            res = vocabs.check_global_attribute(ds, attr, property="canonical_name")
            score += res

            if res == 0:
                messages.append("Required '{}' global attribute is not present.".format(attr))
            elif res == 1:
                messages.append("Required '{}' global attribute value is invalid.".format(attr))

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)