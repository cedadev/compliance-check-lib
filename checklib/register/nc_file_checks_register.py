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
from checklib.code.errors import FileError, ParameterError


class NCFileCheckBase(CallableCheckBase):
    "Base class for all NetCDF4 File Checks (that work on a file path."

    def _check_primary_arg(self, primary_arg):
        if not isinstance(primary_arg, Dataset):
            raise FileError("Object for testing is not a netCDF4 Dataset: {}".format(str(primary_arg)))


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
            raise ParameterError("Keyword arguments for Global Attribute Regex Check must include ('attribute', 'regex').")

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
            raise ParameterError("Keyword arguments for Global Attribute Vocab Check must include ('attribute').")


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


class MainVariableAttributeCheck(NCFileCheckBase):
    """
    Finds main variable and checks attribute '{attr_name}' has required value: '{attr_value}'.
    """
    short_name = "Main variable attribute"
    defaults = {}
    message_templates = ["Cannot identify main variable to examine attributes",
                         "Required variable attribute '{attr_name}' is not present for variable: '{attr_value}'.",
                         "Required variable attribute '{attr_name}' has incorrect value '{attr_value}' for main "
                         "variable."
                         ]
    level = "HIGH"


    def _setup(self):
        "Checks that required arguments have been provided."
        required_args = ("attr_name", "attr_value")
        for arg in required_args:
            if arg not in self.kwargs:
                raise ParameterError("Keyword arguments for NC Variable Metadata Check must "
                                     "contain: '{}'.".format(arg))


    def _get_result(self, primary_arg):
        ds = primary_arg

        score = 0
        messages = []

        # Check main variable is identifiable first
        try:
            variable = nc_util.get_main_variable(ds)
            score += 1
        except:
            messages = [self.get_messages()[score]]
            return Result(self.level, (score, self.out_of),
                          self.get_short_name(), messages)

        # Now check attribute
        attr_name = self.kwargs["attr_name"]

        if attr_name not in variable.ncattrs():
            messages = [self.get_messages()[score]]

        else:
            score += 1
            # Check the value of attribute

            expected_value = self.kwargs["attr_value"]
            check = nc_util.check_nc_attribute(variable, attr_name, expected_value)

            if check:
                score += 1
            else:
                messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)



class ValidGlobalAttrsMatchFileNameCheck(NCFileCheckBase):
    """
    All components in the file name must either be set as global attributes in
    the NetCDF file and must be valid terms in the relevant controlled
    vocabulary, or match the given regular expression(s).

    The score is made up of:
      - 1 for the file extension
      - 2 per global attribute (exists and is valid)
      - 1 per file-name component / regular expression (valid)
      -
    """
    short_name = "Global attributes match file name/vocab"
    defaults = {"delimiter": "_", "extension": ".nc", "ignore_attr_checks": None}
    message_templates = ["File name does not match global attributes.",
                         "Each global attribute is checked separately."]
    level = "HIGH"

    def _setup(self):
        """
        Uses the instructions given about the order of the file name components
        to work out the 'out of' value for the result.

        The delimiter is used to split up the file name.

        The extension is the extension of the file name.

        The order should include the list of facets or regex to check the
        components of the file name against. Regex should start with
        'regex:' followed by the regex.
        """
        not_found = []
        for key in ("delimiter", "extension", "order"):
            if key not in self.kwargs:
                not_found.append(key)

        if not_found:
            raise ParameterError("Keyword arguments for check must include: {}.".format(not_found))

        # Sort out order of items to check in file name
        self.kwargs["order"] = self.kwargs["order"].split("~")

        # Set self.out_of starting at 1 - for the extension check
        self.out_of = 1
        for order in self.kwargs["order"]:
            if order.startswith('regex:'):
                self.out_of += 1
            else:
                self.out_of += 3

        # Overwrite "ignore_attr_checks" if None
        if not self.kwargs["ignore_attr_checks"]:
            self.kwargs["ignore_attr_checks"] = []
        else:
            for ignore in self.kwargs["ignore_attr_checks"]:
                print ignore, self.kwargs['order']
                if ignore not in self.kwargs["order"]:
                    raise ParameterError("Invalid arguments: requested to ignore attribute " 
                                         "not provided in 'order': {}.".format(ignore))
                # Decrement `out_of` because we won't check this attribute
                self.out_of -= 2


    def _get_result(self, primary_arg):
        ds = primary_arg

        score = 0
        messages = []

        vocabs = ESSVocabs(*self.vocabulary_ref.split(":")[:2])
        fname = os.path.basename(ds.filepath())

        fn_score, msg = vocabs.check_file_name(fname, keys=self.kwargs["order"],
                                               delimiter=self.kwargs["delimiter"],
                                               extension=self.kwargs["extension"])
        score += fn_score
        if fn_score < (self.out_of / 3.):
            # a third of the marks are for the file name check
            messages.extend(msg)

        # Check global attributes one-by-one
        items = os.path.splitext(fname)[0].split(self.kwargs["delimiter"])

        for i, attr in enumerate(self.kwargs["order"]):
            if attr.startswith('regex:') or attr in self.kwargs["ignore_attr_checks"]:
                # Case 1: we do not have the attribute name - so cannot check
                # Case 2: instructed to not perform this check
                continue
            res, msg = vocabs.check_global_attribute_value(ds, attr, items[i],
                                                           property="raw_name")
            score += res

            if res < 2:
                messages.extend(msg)

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)
                      

class VariableExistsInFileCheck(NCFileCheckBase):
    """
    Variable {var_id} exists in NetCDF file.
    """
    short_name = "Variable exists: {var_id}"
    defaults = {}
    message_templates = ["Required variable {var_id} is not present."]
    level = "HIGH"


    def _get_result(self, primary_arg):
        ds = primary_arg

        score = 0
        if nc_util.is_variable_in_dataset(ds, self.kwargs["var_id"]):
            score = 1
            
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)
                      
                      
class VariableRangeCheck(NCFileCheckBase):
    """
    The variable {var_id} must have values in the range {minimum}
    to {maximum}.
    """
    short_name = "Variable range {var_id}: {minimum} to {maximum}"
    defaults = {}
    message_templates = ["Variable {var_id} does not exist.",
                         "Variable {var_id} has values outside the permitted range: "
                         "{minimum} to {maximum}"]
    level = "HIGH"


    def _get_result(self, primary_arg):
        ds = primary_arg
        var_id = self.kwargs["var_id"]
        mn, mx = self.kwargs["minimum"], self.kwargs["maximum"]

        score = 0
        if nc_util.is_variable_in_dataset(ds, var_id):
            score = 1

        if nc_util.variable_is_within_valid_bounds(ds, var_id, mn, mx):
            score += 1      
            
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class _VariableTypeCheckBase(NCFileCheckBase):
    """
    Base (abstract) class for building variable type checks.
    """
    defaults = {}
    level = "HIGH"

    def _check_kwargs(self, req_args):
        "Checks required keyword args are present."

        for kwarg in req_args:
            if kwarg not in self.kwargs:
                raise ParameterError("Keyword arguments for Variable Type Check must include ('{0}').".format(kwarg))

    def _package_result(self, success):
        "Package up result depending on success (boolean)."
        messages = []

        if success:
            score = self.out_of
        else:
            score = 0
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class VariableTypeCheck(_VariableTypeCheckBase):
    """
    The variable {var_id} must be of type: {dtype}.
    """
    short_name = "Variable data type: {var_id}"
    message_templates = ["The variable {var_id} was not of the required type: {dtype}"]

    def _setup(self):
        "Checks that required args are provided"
        req_args = ("var_id", "dtype")
        self._check_kwargs(req_args)

    def _get_result(self, primary_arg):
        ds = primary_arg
        success = nc_util.check_variable_type(ds, self.kwargs["var_id"], self.kwargs["dtype"])
        return self._package_result(success)


class MainVariableTypeCheck(_VariableTypeCheckBase):
    """
    The main variable must be of type: {dtype}.
    """
    short_name = "Main variable data type"
    message_templates = ["Main variable was not of the required type: {dtype}"]

    def _setup(self):
        "Checks that required args are provided"
        req_args = ("dtype",)
        self._check_kwargs(req_args)

    def _get_result(self, primary_arg):
        ds = primary_arg
        success = nc_util.check_main_variable_type(ds, self.kwargs["dtype"])
        return self._package_result(success)


class NCVariableMetadataCheck(NCFileCheckBase):
    """
    The variable '{var_id}' must exist in the file with the attributes defined in the
    controlled vocabulary specified.
    """
    short_name = "Variable metadata: {var_id}"
    defaults = {}
    message_templates = ["Variable '{var_id}' not found in the file so cannot perform other checks.",
                         "Each variable attribute is checked separately."]

    level = "HIGH"

    def _setup(self):
        "Checks that required arguments have been provided."
        required_args = ("var_id", "pyessv_namespace")
        for arg in required_args:
            if arg not in self.kwargs:
                raise ParameterError("Keyword arguments for NC Variable Metadata Check must "
                                     "contain: '{}'.".format(arg))


    def _get_result(self, primary_arg):
        ds = primary_arg
        var_id = self.kwargs["var_id"]

        # First, work out the overall 'out of' value based on number of attributes
        vocabs = ESSVocabs(*self.vocabulary_ref.split(":")[:2])
        lookup = ":".join([self.kwargs["pyessv_namespace"], var_id])
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
                check = nc_util.check_nc_attribute(variable, attr, expected_value)
                if check:
                    score += 1
                else:
                    messages.append("Required variable attribute '{}' has incorrect value ('{}') "
                                    "for variable: '{}'. Value should be: '{}'.".format(attr,
                                                                                        getattr(variable, attr), var_id,
                                                                                        expected_value))

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class NetCDFFormatCheck(NCFileCheckBase):
    """
    The NetCDF sub-format must be: {format}.
    """
    short_name = "NetCDF sub-format: {format}"
    defaults = {}
    message_templates = ["The NetCDF sub-format must be: {format}."]

    level = "HIGH"

    def _setup(self):
        "Checks that the `format` argument has been provided."
        if "format" not in self.kwargs:
            raise ParameterError("Keyword argument 'format' is required for NetCDF Format Check.")


    def _get_result(self, primary_arg):
        ds = primary_arg
        file_format = getattr(ds, "file_format", None)

        score = 0
        if file_format == self.kwargs["format"]:
            score = 1

        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class NetCDFDimensionCheck(NCFileCheckBase):
    """
    The file must contain dimension and coordinate variable: {}.
    """
    short_name = "NetCDF dimension: {dim_id}"
    defaults = {}
    message_templates = ["Dimension not found: {dim_id}.",
                         "Dimension '{dim_id}' does not have required length",
                         "Coordinate variable for dimension not found: {dim_id}.",
                         "Coordinate variable for dimension '{dim_id}' does not have expected properties."]

    level = "HIGH"

    def _setup(self):
        "Checks that the required arguments have been provided."
        if "dim_id" not in self.kwargs:
            raise ParameterError("Keyword argument 'dim_id' is required for NetCDF Dimension Check.")

        if "pyessv_namespace" not in self.kwargs:
            raise ParameterError("Keyword argument 'pyessv_namespace' is required for NetCDF Dimension Check.")


    def _get_result(self, primary_arg):
        ds = primary_arg
        dim_id = self.kwargs["dim_id"]

        score = 0
        messages = []

        if dim_id in ds.dimensions:
            score += 1
            self.out_of = 1
        else:
            messages = [self.get_messages()[score],
                        "Cannot look up coordinate variable because dimension does not exist.",
                        "Cannot assess coordinate variable properties because dimension does not exist."]
            self.out_of = len(messages)

            # Now return because all other checks are irrelevant
            return Result(self.level, (score, self.out_of), self.get_short_name(), messages)

        # Now test coordinate variable using look-up in vocabularies
        # First, work out the overall 'out of' value based on number of attributes
        vocabs = ESSVocabs(*self.vocabulary_ref.split(":")[:2])
        lookup = ":".join([self.kwargs["pyessv_namespace"], dim_id])
        expected_attr_dict = vocabs.get_value(lookup, "data")

        # Check length if needed
        if "length" in expected_attr_dict:
            req_length = expected_attr_dict["length"]

            if req_length == ds.dimensions[dim_id].size:
                score += 1
            else:
                messages.append("Dimension '{}' does not have required length: {}.".format(dim_id, req_length))

            self.out_of += 1

        # Check coordinate variable exists for dimension
        if dim_id in ds.variables:
            score += 1
            self.out_of += 1

            variable = ds.variables[dim_id]

            # Check the coordinate variable attributes one-by-one
            for attr, expected_value in expected_attr_dict.items():
                # Length has already been checked - so ignore here
                if attr == "length": continue

                self.out_of += 1

                if attr not in variable.ncattrs():
                    messages.append("Required variable attribute '{}' is not present for "
                                    "coorinate variable: '{}'.".format(attr, dim_id))
                else:
                    score += 1
                    self.out_of += 1

                    # Check the value of attribute
                    check = nc_util.check_nc_attribute(variable, attr, expected_value)
                    if check:
                        score += 1
                    else:
                        messages.append("Required variable attribute '{}' has incorrect value ('{}') "
                                        "for variable: '{}'. Value should be: '{}'.".format(attr,
                                        getattr(variable, attr), dim_id, expected_value))
        else:
            messages.append("Coordinate variable for dimension not found: {}.".format(dim_id))
            self.out_of += 1

        return Result(self.level, (score, self.out_of), self.get_short_name(), messages)