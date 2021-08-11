import pytest
import os
from .fixtures.live import *
from .fixtures.auth_v2 import *
from .fixtures.reactor import *
from .fixtures.monkeypatch import *


@pytest.fixture(scope="function")
def change_test_dir(request):
    def func(dirname=None):
        if dirname is None:
            dirname = request.fspath.dirname
        os.chdir(dirname)

    yield func
    os.chdir(request.config.invocation_dir)

