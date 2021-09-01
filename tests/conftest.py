import logging
import pytest
import os
from .fixtures.live import *
from .fixtures.auth_v2 import *
from .fixtures.reactor import *
from .fixtures.monkeypatch import *
from .fixtures.log import *


@pytest.fixture(scope="function")
def change_test_dir(request):
    def func(dirname=None):
        if dirname is None:
            dirname = request.fspath.dirname
        logging.debug(f"changing dir to {dirname}")
        os.chdir(dirname)

    yield func
    og = request.config.invocation_dir
    logging.debug(f"changing dir to {og}")
    os.chdir(og)

