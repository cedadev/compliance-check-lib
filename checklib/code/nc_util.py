"""
nc_util.py
=========

Utilities to support compliance checker classes - working with
netCDF4 Dataset objects.

"""

import re
import numpy as np


def is_there_only_one_main_variable(ds):
    """
    Checks variables in a NetCDF Dataset and returns boolean regarding
    whether there is only one main variable. It believes the main variable
    has the biggest shape/size. If two are the same size it returns False.

    :param ds: netCDF4 Dataset object
    :return: boolean
    """
    dsv = ds.variables
    sizes = [dsv[ncvar].size for ncvar in dsv]

    if sizes.count(max(sizes)) > 1:
        return False

    return True


def check_global_attr_against_regex(ds, attr, regex):
    """
    Returns 0 if attribute `attr` not found, 1 if found but doesn't match
    and 2 if found and matches `regex`.

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :regex: a regular expression definition [string]
    :return: an integer (see above)
    """
    if attr not in ds.ncattrs():
        return 0
    if not re.match("^{}$".format(regex), getattr(ds, attr)):
        return 1
    # Success
    return 2


def check_main_variable_type(ds, datatype):
    """
    Checks variables in a NetCDF Dataset and returns boolean regarding
    whether the main variable is of the required type. The main
    variable is determined as that which has the biggest shape/size.

    :param ds: netCDF4 Dataset object
    :paran datatype: the type of the variable, this should be a numpy type: string
    :return: boolean
    """
    dsv = ds.variables
    size = 0
    for ncvar in dsv:
        if dsv[ncvar].size > size:
            main_var = ncvar
            size = dsv[ncvar].size

    return dsv[main_var].dtype == np.dtype(datatype)


def check_variable_type(ds, var_id, datatype):
    """
    Checks variables in a NetCDF Dataset and returns boolean regarding
    whether the variable `var_id` is of the required type.

    :param ds: netCDF4 Dataset object
    :param var_id: Variable ID.
    :paran datatype: the type of the variable, this should be a numpy type: string
    :return: boolean
    """
    variable = ds.variables[var_id]
    return variable.dtype == np.dtype(datatype)


def is_variable_in_dataset(ds, var_id):
    """
    Checks that variable with name `var_id` exists in the file.
    Returns True if variable is in the dataset.

    :param ds: netCDF4 Dataset object
    :paran var_id: the variable ID. 
    :return: boolean
    """
    return var_id in ds.variables


def variable_is_within_valid_bounds(ds, var_id, minimum, maximum):
    """
    Checks whether variable `var_id` is out of bounds set by arguments
    `minimum` and `maximum`.

    :param ds: netCDF4 Dataset object
    :paran var_id: the variable ID.
    :param minimum: the minimum allowed value (a number)
    :param maximum: the maximum allowed value (a number)
    :return: boolean
    """
    if var_id not in ds.variables: return False

    data = ds.variables[var_id][:]
    mn, mx = data.min(), data.max()

    if mn < minimum or mx > maximum:
        return False

    return True 
