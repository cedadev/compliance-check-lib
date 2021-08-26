from pathlib import Path

COMP_CHECK_CV_REPO_DIR = Path.home() / ".comp-check-cvs-cache"
COMP_CHECK_CV_CACHE_DIR = (COMP_CHECK_CV_REPO_DIR / "master" / "pyessv-archive-eg-cvs").as_posix()
EG_DATA_DIR = "tests/example_data"

