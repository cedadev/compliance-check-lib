"""
test_ess_vocab_checks.py
========================

Unit tests for the contents of the checklib.cvs.ess_vocabs module.

"""

import pytest
from netCDF4 import Dataset
import checklib.cvs.ess_vocabs as ess_vocabs


@pytest.mark.ukcp
def test_get_value_string_lookup_success_1_ukcp(load_check_test_cvs):
    x = ess_vocabs.ESSVocabs('ukcp', 'ukcp18')
    resp = x.get_value('variable:tasAnom')
    assert(resp == 'tasAnom')

    # Check full term path works
    resp = x.get_value('ukcp:ukcp18:variable:tasAnom')
    assert(resp == 'tasAnom')


@pytest.mark.ukcp
def test_get_value_string_lookup_data_success_2_ukcp(load_check_test_cvs):
    x = ess_vocabs.ESSVocabs('ukcp', 'ukcp18')
    resp = x.get_value('coordinate:time', property='data')

    assert("units" in resp)
    assert(resp['units'] == 'days since 1970-01-01 00:00:00')


@pytest.mark.ncas
def test_get_value_string_lookup_success_3_ncas(load_check_test_cvs):
    x = ess_vocabs.ESSVocabs('ncas', 'amf')
    resp = x.get_value('product:dew-point')
    assert(resp == 'dew-point')

    # Check full term path works
    resp = x.get_value('ncas:amf:product:dew-point')
    assert(resp == 'dew-point')


@pytest.mark.ukcp
def test_get_value_string_lookup_failure_1(load_check_test_cvs):
    x = ess_vocabs.ESSVocabs('ukcp', 'ukcp18')
    lookup = 'domain:dog'
    try:
        x.get_value(lookup)
    except Exception as err:
        assert(str(err) == "Could not get value of term based on vocabulary lookup: '{}'.".format(lookup))


@pytest.mark.ukcp
def test_get_terms(load_check_test_cvs):
    x = ess_vocabs.ESSVocabs('ukcp', 'ukcp18')
    collection = 'river_basin'
    terms = x.get_terms(collection)

    assert(str(terms[-1]) == 'ukcp:ukcp18:river-basin:western-wales')
    import pyessv
    assert(isinstance(terms[-1], pyessv.Term))

    # Check alphabetical
    terms_strings = [str(term) for term in terms]
    alpha_terms_strings = sorted(terms_strings)
    assert(terms_strings == alpha_terms_strings)


@pytest.mark.ukcp
def test_get_terms_fail(load_check_test_cvs):
    x = ess_vocabs.ESSVocabs('ukcp', 'ukcp18')
    collection = 'RUBBISH'
    with pytest.raises(Exception):
        x.get_terms(collection)

