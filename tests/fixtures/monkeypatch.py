import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture(scope="session")
def monkeysession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()