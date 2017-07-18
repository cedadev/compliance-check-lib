"""
test_nc_file_checks.py
======================

Unit tests for the contents of the checklib.register.nc_file_checks module.

"""

from checklib.code.errors import ParameterError
from checklib.register.nc_file_checks_register import *
from netCDF4 import Dataset


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


# ValidGlobalAttrsMatchFileNameCheck - SUCCESS
def test_ValidGlobalAttrsMatchFileNameCheck_success_1():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "institution_id~realm~frequency"},
                                           vocabulary_ref="eustace-team:eustace")
    ds = Dataset(
        'checklib/test/example_data/nc_file_checks_data/mohc_ocean_day.nc')
    resp = x(ds)
    assert(resp.value == (9, 9)), resp.msgs


def test_ValidGlobalAttrsMatchFileNameCheck_success_2():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "frequency"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset('checklib/test/example_data/nc_file_checks_data/day.nc')
    resp = x(ds)
    assert(resp.value == (3, 3)), resp.msgs


def test_ValidGlobalAttrsMatchFileNameCheck_success_3():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "scenario"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset('checklib/test/example_data/nc_file_checks_data/sres-a1b.nc')
    resp = x(ds)
    assert(resp.value == (3, 3)), resp.msgs


def test_ValidGlobalAttrsMatchFileNameCheck_success_4():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "frequency"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset('checklib/test/example_data/nc_file_checks_data/day.nc')
    resp = x(ds)
    assert(resp.value == (3, 3)), resp.msgs


def test_ValidGlobalAttrsMatchFileNameCheck_success_5():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "regex:^(?:\d{2}){2,6}(?:$|-(?:\d{2}){2,6}$)"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset(
        'checklib/test/example_data/nc_file_checks_data/19981201-19991131.nc')
    resp = x(ds)
    assert(resp.value == (1, 1)), resp.msgs


def test_ValidGlobalAttrsMatchFileNameCheck_success_6():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "variable_id~scenario~dataset_id~prob_type~frequency~regex:^(?:\d{2}){2,6}(?:$|-(?:\d{2}){2,6}$)"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset(
        'checklib/test/example_data/nc_file_checks_data/temp-max_sres-a1b_ukcp18-land-prob-25km_sample_day_19981201-19991130.nc')
    resp = x(ds)
    assert(resp.value == (16, 16)), resp.msgs


# ValidGlobalAttrsMatchFileNameCheck - FAIL

# Invalid collection identifier
# Required 'duff' global attribute is not present.
def test_ValidGlobalAttrsMatchFileNameCheck_fail_1():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "duff"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset('checklib/test/example_data/nc_file_checks_data/day.nc')
    resp = x(ds)
    assert(resp.value == (0, 3)), resp.msgs


# File name does not match global attributes.
# Required 'frequency' global attribute value 'day' not equal value from
# file name 'duff'.
def test_ValidGlobalAttrsMatchFileNameCheck_fail_2():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "frequency"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset('checklib/test/example_data/nc_file_checks_data/duff.nc')
    resp = x(ds)
    assert(resp.value == (1, 3)), resp.msgs


# Required 'frequency' global attribute value 'year' not equal value from
# file name 'day'.
def test_ValidGlobalAttrsMatchFileNameCheck_fail_3():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "frequency~regex:\w"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset('checklib/test/example_data/nc_file_checks_data/day_duff1.nc')
    resp = x(ds)
    assert(resp.value == (3, 4)), resp.msgs


# Required 'frequency' global attribute value 'duff' not equal value from file name 'day'.
# Required 'frequency' global attribute value 'duff' is invalid.
def test_ValidGlobalAttrsMatchFileNameCheck_fail_4():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "frequency~regex:\w"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset('checklib/test/example_data/nc_file_checks_data/day_duff2.nc')
    resp = x(ds)
    assert(resp.value == (3, 4)), resp.msgs


# Required 'frequency' global attribute is not present.
def test_ValidGlobalAttrsMatchFileNameCheck_fail_5():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "frequency~regex:\w"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset('checklib/test/example_data/nc_file_checks_data/day_duff3.nc')
    resp = x(ds)
    assert(resp.value == (2, 4)), resp.msgs

# File name fragment 19981201-19991131 does not match regex ^(?:\\d{2}){2,3}(?:$|-(?:\\d{2}){2,6}$).
def test_ValidGlobalAttrsMatchFileNameCheck_fail_6():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "regex:^(?:\d{2}){2,3}(?:$|-(?:\d{2}){2,6}$)"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset(
        'checklib/test/example_data/nc_file_checks_data/19981201-19991131.nc')
    resp = x(ds)
    assert(resp.value == (0, 1)), resp.msgs


# File name fragment 19981201-19991131 does not match regex ^(?:\\d{2}){2,3}(?:$|-(?:\\d{2}){2,6}$).
def test_ValidGlobalAttrsMatchFileNameCheck_fail_7():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "variable_id~scenario~dataset_id~prob_type~frequency~regex:^(?:\d{2}){2,6}(?:$|-(?:\d{2}){2,3}$)"},
                                           vocabulary_ref="ukcp:ukcp18")
    ds = Dataset(
        'checklib/test/example_data/nc_file_checks_data/temp-max_sres-a1b_ukcp18-land-prob-25km_sample_day_19981201-19991130.nc')
    resp = x(ds)
    assert(resp.value == (15, 16)), resp.msgs


# Object for testing is not a netCDF4 Dataset: missing.nc
def test_ValidGlobalAttrsMatchFileNameCheck_fail_8():
    x = ValidGlobalAttrsMatchFileNameCheck(kwargs={"delimiter": "_",
                                                   "extension": ".nc",
                                                   "order": "regex:^(?:\d{2}){2,3}(?:$|-(?:\d{2}){2,6}$)"},
                                           vocabulary_ref="ukcp:ukcp18")
    resp = x("missing.nc")
    assert(resp.value == (0, 1)), resp.msgs


def test_ValidGlobalAttrsMatchFileNameCheck_fail_9():
    try:
        ValidGlobalAttrsMatchFileNameCheck(kwargs={"x": "_",
                                                   "xx": ".nc",
                                                   "xxx": "regex:^(?:\d{2}){2,3}(?:$|-(?:\d{2}){2,6}$)"},
                                           vocabulary_ref="ukcp:ukcp18")
    except Exception as ex:
        assert(type(ex) == ParameterError), 'Expecting ParameterError, but got {}'.format(type(ex))
    else:
        assert(False), "Expecting ParameterError, but no exception raised"


# MainVariableTypeCheck - SUCCESS
def test_MainVariableTypeCheck_success_1():
    x = MainVariableTypeCheck(kwargs={"dtype": "float32"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert(resp.value == (1, 1)), resp.msgs


# MainVariableTypeCheck - FAIL

# 'Main variable was not the required type: float64
def test_MainVariableTypeCheck_fail_1():
    x = MainVariableTypeCheck(kwargs={"dtype": "float64"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/simple_nc.nc'))
    assert(resp.value == (0, 1)), resp.msgs


def test_MainVariableTypeCheck_fail_2():
    try:
        MainVariableTypeCheck(kwargs={"dtypeXXXX": "float64"})
    except Exception as ex:
        assert(type(ex) == ParameterError), 'Expecting ParameterError, but got {}'.format(type(ex))
    else:
        assert(False), "Expecting ParameterError, but no exception raised"

