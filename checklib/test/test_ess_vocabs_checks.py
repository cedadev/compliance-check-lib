"""
test_ess_vocab_checks.py
========================

Unit tests for the contents of the checklib.cvs.ess_vocabs module.

"""

# Set local directory as store for `pyessv-archive` controlled vocabs
# MUST DO THIS BEFORE other imports
import os
os.environ['PYESSV_ARCHIVE_HOME'] = 'checklib/test/example_data/pyessv-archive-eg-cvs'

from checklib.cvs.ess_vocabs import *
from netCDF4 import Dataset


def test_get_value_string_lookup_success_1():
    x = ESSVocabs('ncas', 'amf')
    resp = x.get_value('common-land-variable:day-of-year')
    assert(resp == 'day_of_year')

    # Check full term path works
    resp = x.get_value('ncas:amf:common-land-variable:day-of-year')
    assert(resp == 'day_of_year')


def test_get_value_string_lookup_failure_1():
    x = ESSVocabs('ncas', 'amf')

    try:
        x.get_value('common-land-variable:day-of-year')
    except Exception, err:
        assert(str(err) == "Could not get value of term based on lookup: 'common-land-variable:day-of-year'.")


def test_get_value_string_lookup_data_success_2():
    x = ESSVocabs('ncas', 'amf')
    resp = x.get_value('common-land-variable:time', property='data')
    assert(resp['units'] == 'seconds since 1970-01-01 00:00:00')


def test_get_value_string_lookup_amf_complex_success():
    x = ESSVocabs('ncas', 'amf')
    resp = x.get_value('common-land-variable:time', 'data')
    assert("units" in resp)

    resp = x.get_value('common-land-dimension:time', 'data')
    assert("units" in resp)