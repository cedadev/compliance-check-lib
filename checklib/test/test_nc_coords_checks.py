"""
test_nc_coords_checks.py
======================

Unit tests for the contents of the checklib.register.nc_coords_checks_register module.

"""

import pytest
from netCDF4 import Dataset

from checklib.register.nc_coords_checks_register import *


def test_NCCoordVarHasBoundsCheck_success_1():
    x = NCCoordVarHasBoundsCheck(kwargs={"var_id": "lat"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/cmip5_example_1.nc'))
    assert(resp.value == (2, 2))


def test_NCCoordVarHasBoundsCheck_fail_1():
    x = NCCoordVarHasBoundsCheck(kwargs={"var_id": "RUBBISH"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/cmip5_example_1.nc'))
    assert(resp.value == (0, 2))

    x = NCCoordVarHasBoundsCheck(kwargs={"var_id": "height"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/cmip5_example_1.nc'))
    assert(resp.value == (1, 2))

