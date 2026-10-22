from pathlib import Path
from sqlite3 import OperationalError

from pytest import raises

from overcast.storage import check_database


def test_check_storage(tmp_path: Path) -> None:
    path = tmp_path / "app.sqlite"
    result = check_database(path)

    assert path.is_file()
    assert result == (1,)


def test_check_missing_dir(tmp_path: Path) -> None:
    path = tmp_path / "missing" / "app.sqlite"

    with raises(OperationalError):
        check_database(path)

    assert not path.parent.exists()
