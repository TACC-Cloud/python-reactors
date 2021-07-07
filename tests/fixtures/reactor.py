import pytest
from reactors.runtime import Reactor


@pytest.fixture
@pytest.mark.usefixtures(('abaco_access_token', 'abaco_username', 'abaco_api_server'))
def r() -> Reactor:
    """Returns an instantiated Reactor instance with a bare `client` attribute
    initialized from Tapis v2 credentials in env vars.
    """
    return Reactor()