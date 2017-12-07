"""
test_ess_vocab_checks.py
========================

Unit tests for the contents of the checklib.cvs.ess_vocabs module.

"""

from checklib.cvs.ess_vocabs import *
from netCDF4 import Dataset


def test_get_value_string_lookup_success_1():
    x = ESSVocabs('ncas', 'amf')
    resp = x.get_value('variable:day-of-year')
    assert(resp == 'day_of_year')

    # Check full term path works
    resp = x.get_value('ncas:amf:variable:day-of-year')
    assert(resp == 'day_of_year')


def test_get_value_string_lookup_failure_1():
    x = ESSVocabs('ncas', 'amf')

    try:
        resp = x.get_value('day-of-year')
    except Exception, err:
        assert(str(err) == "Could not get value of term based on lookup: 'day-of-year'.")


def test_get_value_string_lookup_data_success_2():
    x = ESSVocabs('ncas', 'amf')
    resp = x.get_value('variable:time', property='data')
    assert(resp['units'] == 'seconds since 1970-01-01 00:00:00 UTC')

