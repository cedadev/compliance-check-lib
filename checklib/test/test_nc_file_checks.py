"""
test_nc_file_checks.py
======================

Unit tests for the contents of the checklib.register.nc_file_checks module.

"""

from netCDF4 import Dataset

from checklib.register.nc_file_checks_register import *


def test_GlobalAttrRegexCheck_success_1():
    x = GlobalAttrRegexCheck(kwargs={"attribute": "Conventions", "regex": "CF-\d+\.\d+"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert(resp.value == (2, 2))

def test_GlobalAttrRegexCheck_success_2():
    x = GlobalAttrRegexCheck(kwargs={"attribute": "source", "regex": ".{4,}"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert (resp.value == (2, 2))

def test_GlobalAttrRegexCheck_success_3():
    x = GlobalAttrRegexCheck(kwargs={"attribute": "project_id", "regex": "EUSTACE"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert (resp.value == (2, 2))

def test_GlobalAttrRegexCheck_success_4():
    x = GlobalAttrRegexCheck(kwargs={"attribute": "contact", "regex": ".{4,}"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert (resp.value == (2, 2))

def test_GlobalAttrRegexCheck_success_5():
    x = GlobalAttrRegexCheck(kwargs={"attribute": "creator_email", "regex": ".+@.+\..+"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert (resp.value == (2, 2))

def test_GlobalAttrRegexCheck_success_6():
    x = GlobalAttrRegexCheck(kwargs={"attribute": "creation_date", "regex": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert (resp.value == (2, 2))

def test_GlobalAttrRegexCheck_fail_1():
    x = GlobalAttrRegexCheck(kwargs={"attribute": "sausages", "regex": "CF-\d+\.\d+"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert(resp.value == (0, 2))
    assert(resp.msgs[0] == "Required 'sausages' global attribute is not present.")

def test_GlobalAttrRegexCheck_fail_2():
    x = GlobalAttrRegexCheck(kwargs={"attribute": "Conventions", "regex": "garbage - CF-\d+\.\d+"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert(resp.value == (1, 2))

def test_GlobalAttrVocabCheck_success_1():
    x = GlobalAttrVocabCheck(kwargs={"attribute": "frequency", "vocab_lookup": "canonical_name"},
                             vocabulary_ref="eustace-team:eustace:frequency")
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert (resp.value == (2, 2))

def test_GlobalAttrVocabCheck_success_2():
    x = GlobalAttrVocabCheck(kwargs={"attribute": "institution_id", "vocab_lookup": "description"},
                             vocabulary_ref="eustace-team:eustace:institution_id")
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert (resp.value == (2, 2))

def test_GlobalAttrVocabCheck_success_3():
    x = GlobalAttrVocabCheck(kwargs={"attribute": "institution", "vocab_lookup": "data.postalAddress"},
                             vocabulary_ref="eustace-team:eustace:institution_id")
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert (resp.value == (2, 2))

def test_GlobalAttrVocabCheck_fail_1():
    x = GlobalAttrVocabCheck(kwargs={"attribute": "frequency", "vocab_lookup": "canonical_name"},
                             vocabulary_ref="eustace-team:eustace")
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/two_vars_nc.nc'))
    assert (resp.value == (1, 2))

def test_OneMainVariablePerFileCheck_success():
    x = OneMainVariablePerFileCheck(kwargs={})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert(resp.value == (1, 1))

def test_OneMainVariablePerFileCheck_fail():
    x = OneMainVariablePerFileCheck(kwargs={})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/two_vars_nc.nc'))
    assert(resp.value == (0, 1))

def test_ValidGlobalAttrsMatchFileNameCheck_success_1():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_", "extension": ".nc",
                                                   "order": "institution_id,realm,frequency"},
                                           vocabulary_ref="eustace-team:eustace")
    ds = Dataset('checklib/test/example_data/nc_file_checks_data/mohc_ocean_day.nc')
    resp = x(ds)
    assert(resp.value == (7, 7))
