import pytest
import os


@pytest.fixture
def loggly_url(monkeypatch):
    if "_REACTOR_LOGGLY_URL" in os.environ:
        return os.environ['_REACTOR_LOGGLY_URL']
    elif '_REACTOR_LOGGLY_TOKEN' in os.environ:
        token = os.environ['_REACTOR_LOGGLY_TOKEN']
        return f'https://logs-01.loggly.com/inputs/{token}/tag/python'
    raise ValueError(f"neither _REACTOR_LOGGLY_URL nor "
                        "_REACTOR_LOGGLY_TOKEN are set in test env")
