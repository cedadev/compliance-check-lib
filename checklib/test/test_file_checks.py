"""
test_file_checks.py
===================

Unit tests for the contents of the checklib.register.file_checks_register module.

"""

from checklib.register.file_checks_register import *


def test_FileSizeCheck_soft_fail():
    x = FileSizeCheck(kwargs={"threshold": 1e-15, "severity": "soft"})
    resp = x('README.md')
    assert(resp.value == (0, 1))

def test_FileSizeCheck_soft_success():
    x = FileSizeCheck(kwargs={"severity": "soft"})
    resp = x('README.md')
    assert(resp.value == (1, 1))

def test_FileSizeCheck_hard_fail():
    x = FileSizeCheck(kwargs={"threshold": 1e-15, "severity": "hard"})
    resp = x('README.md')
    assert(resp.value == (0, 1))

def test_FileSizeCheck_hard_success():
    x = FileSizeCheck(kwargs={"threshold": 4, "severity": "hard"})
    resp = x('README.md')
    assert(resp.value == (1, 1))
    
def test_FileNameStructureCheck_success():
    good = [
        ("checklib/test/example_data/file_checks_data/good_file.nc", {}),
        ("checklib/test/example_data/file_checks_data/good_file_as_text.txt", {"delimiter": "_",
                                                                               "extension": ".txt"})
        ]

    for fpath, kwargs in good:
        x = FileNameStructureCheck(kwargs)
        resp = x(fpath)
        assert(resp.value == (1, 1))

def test_FileNameStructureCheck_fail():
    bad = [
        ("checklib/test/example_data/file_checks_data/_bad_file1.nc", {}),
        ("checklib/test/example_data/file_checks_data/bad--file2.nc", {"delimiter": "-",
                                                                      "extension": ".nc"}),
    ]
    for fpath, kwargs in bad:
        x = FileNameStructureCheck(kwargs)
        resp = x(fpath)
        assert(resp.value == (0, 1))
