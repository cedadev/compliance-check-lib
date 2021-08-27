import os

import pytest
from git import Repo

from tests._common import COMP_CHECK_CV_REPO_DIR, COMP_CHECK_CV_CACHE_DIR

COMP_CHECK_TEST_DATA_REPO_URL = "https://github.com/cedadev/cc-vocab-cache"


# Fixture to load mini-esgf-data repository used by roocs tests
@pytest.fixture
def load_check_test_cvs():
    """
    This fixture ensures that the required test controlled vocab repository
    has been cloned to the cache directory within the home directory.
    """
    branch = "master"
    target = os.path.join(COMP_CHECK_CV_REPO_DIR, branch)

    if not os.path.isdir(COMP_CHECK_CV_REPO_DIR):
        os.makedirs(COMP_CHECK_CV_REPO_DIR)

    if not os.path.isdir(target):
        repo = Repo.clone_from(COMP_CHECK_TEST_DATA_REPO_URL, target)
        repo.git.checkout(branch)

    elif os.environ.get("COMP_CHECK_UPDATE_TEST_CVS", "true").lower() != "false":
        repo = Repo(target)
        repo.git.checkout(branch)
        repo.remotes[0].pull()

    # Set the environment variable to point to the directory where 
    # the `pyessv-archive` controlled vocabs are located
    os.environ['PYESSV_ARCHIVE_HOME'] = COMP_CHECK_CV_CACHE_DIR

