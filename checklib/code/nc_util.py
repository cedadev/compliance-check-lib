"""
nc_util.py
=========

Utilities to support compliance checker classes - working with
netCDF4 Dataset objects.

Available attributes of Dataset object are:

[u'_FillValue', '__class__', '__delattr__', '__delitem__', '__doc__', '__format__',
 '__getattr__', '__getattribute__', '__getitem__', '__hash__', '__init__', '__len__',
  '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__',
  '__sizeof__', '__str__', '__subclasshook__', '__unicode__', '_assign_vlen',
  '_cmptype', '_get', '_getdims', '_grp', '_grpid', '_iscompound', '_isprimitive',
  '_isvlen', '_name', '_nunlimdim', '_put', '_toma', '_varid', '_vltype',
  'assignValue', 'chunking', 'datatype', u'date', 'delncattr', 'dimensions',
  'dtype', 'endian', 'filters', 'getValue', 'get_var_chunk_cache', 'getncattr',
  'group', u'long_name', 'maskandscale', u'missing_value', u'name', 'ncattrs',
  'ndim', 'renameAttribute', 'set_auto_maskandscale', 'set_var_chunk_cache',
  'setncattr', 'setncatts', 'shape', 'size', u'source', u'standard_name', u'time',
  u'title', u'units', u'valid_max', u'valid_min']

"""

import re


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
