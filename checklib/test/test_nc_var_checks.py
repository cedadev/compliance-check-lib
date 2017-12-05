"""
test_nc_var_checks.py
======================

Unit tests for the contents of the checklib.register.nc_var_checks_register module.

"""

from checklib.code.errors import ParameterError
from checklib.register.nc_var_checks_register import *
from netCDF4 import Dataset




def test_NCVariableMetadataCheck_partial_success_1():
    x = NCVariableMetadataCheck(kwargs={"var_id": "time"}, vocabulary_ref="ncas:amf")
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert(resp.value == (7, 21))


def test_NCVariableMetadataCheck_fail_1():
    x = NCVariableMetadataCheck(kwargs={"var_id": "day"}, vocabulary_ref="ncas:amf")
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert(resp.value == (0, 15))
    assert(resp.msgs == ["Variable 'day' not found in the file so cannot perform other checks."])


def test_NCVariableMetadataCheck_fail_2():
    x = NCVariableMetadataCheck(kwargs={"var_id": "a-dog?"}, vocabulary_ref="ncas:amf")
    try:
        resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    except Exception, err:
        assert(str(err) == "Could not get value of term based on lookup: 'variables:a-dog?'.")
