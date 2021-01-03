from pathlib import Path
from shutil import copytree

import pytest


@pytest.fixture()
def data_directory(tmp_path: Path, request) -> Path:
    """Fixture that provides a temporary path with data from a directory
    with the same name as the test.
    """
    file = Path(request.module.__file__)
    directory = file.parent / f"{file.stem}.data"

    if Path(directory).is_dir():
        copytree(directory, tmp_path, dirs_exist_ok=True)

    return tmp_path
