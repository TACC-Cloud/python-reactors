import pytest
import os


@pytest.fixture
def loggly_url(monkeypatch):
    if "_TEST_LOGGLY_URL" in os.environ:
        return os.environ['_TEST_LOGGLY_URL']
    elif '_TEST_LOGGLY_CUSTOMER_TOKEN' in os.environ:
        token = os.environ['_TEST_LOGGLY_CUSTOMER_TOKEN']
        return f'https://logs-01.loggly.com/inputs/{token}/tag/python'
    raise ValueError(f"neither _TEST_LOGGLY_URL nor "
                        "_TEST_LOGGLY_CUSTOMER_TOKEN are set in test env")
