import pytest

from clipsy.storage import StorageManager


@pytest.fixture
def storage():
    mgr = StorageManager(db_path=":memory:")
    yield mgr
    mgr.close()
