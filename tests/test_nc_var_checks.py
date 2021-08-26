"""
test_nc_var_checks.py
======================

Unit tests for the contents of the checklib.register.nc_var_checks_register module.

"""

import pytest
from netCDF4 import Dataset

from tests._common import EG_DATA_DIR
from checklib.code.errors import ParameterError
from checklib.register.nc_var_checks_register import *


@pytest.mark.ukcp
def test_NCArrayMatchesVocabTermsCheck_success(load_check_test_cvs):
    x = NCArrayMatchesVocabTermsCheck(kwargs={'var_id': 'geo_region',
                                              'pyessv_namespace': 'river_basin'},
                                      vocabulary_ref='ukcp:ukcp18')
    resp = x(Dataset(f'{EG_DATA_DIR}/river_basin_good_order.nc'))
    assert(resp.value == (1, 1)), resp.msgs


@pytest.mark.ukcp
def test_NCArrayMatchesVocabTermsCheck_fail(load_check_test_cvs):
    x = NCArrayMatchesVocabTermsCheck(kwargs={'var_id': 'geo_region',
                                              'pyessv_namespace': 'river_basin'},
                                      vocabulary_ref='ukcp:ukcp18')
    resp = x(Dataset(f'{EG_DATA_DIR}/river_basin_bad_order.nc'))
    assert(resp.value == (0, 1)), resp.msgs
