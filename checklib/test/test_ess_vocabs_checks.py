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
    x = ESSVocabs('ukcp', 'ukcp18')
    resp = x.get_value('variable:tasAnom')
    assert(resp == 'tasAnom')

    # Check full term path works
    resp = x.get_value('ukcp:ukcp18:variable:tasAnom')
    assert(resp == 'tasAnom')


def test_get_value_string_lookup_data_success_2():
    x = ESSVocabs('ukcp', 'ukcp18')
    resp = x.get_value('coordinate:time', property='data')

    assert("units" in resp)
    assert(resp['units'] == 'days since 1970-01-01 00:00:00')


def test_get_value_string_lookup_failure_1():
    x = ESSVocabs('ukcp', 'ukcp18')
    lookup = 'domain:dog'
    try:
        x.get_value(lookup)
    except Exception, err:
        assert(str(err) == "Could not get value of term based on lookup: '{}'.".format(lookup))

