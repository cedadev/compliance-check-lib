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


def check_main_variable_type(ds, v_type):
    """
    Checks variables in a NetCDF Dataset and returns boolean regarding
    whether the main variable is of the give type. It believes the main
    variable has the biggest shape/size.

    :param ds: netCDF4 Dataset object
    :paran v_type the type of the variable, this should be a numpy type: string
    :return: boolean
    """
    dsv = ds.variables
    size = 0
    for ncvar in dsv:
        if dsv[ncvar].size > size:
            main_var = ncvar
            size = dsv[ncvar].size
    if dsv[main_var].dtype != np.dtype(v_type):
        return False

    return True
