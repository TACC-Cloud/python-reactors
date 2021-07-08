import pytest
from agavepy.agave import Agave
from reactors.runtime import Reactor


@pytest.fixture
def client_v2():
    """Returns active Agave v2 client from credentials cache."""
    tenant_id = 'tacc.prod'
    return Agave._restore_cached(tenant_id=tenant_id)


@pytest.fixture
def token_v2(client_v2) -> str:
    """Supplies an active Tapis v2 token"""
    return client_v2._token


@pytest.fixture
def token_v3() -> str:
    """Supplies an active Tapis v3 token"""
    raise NotImplementedError()


@pytest.fixture()
def abaco_api_server(monkeypatch, client_v2):
    """Sets value of env variable `_abaco_api_server`."""
    # api_server = 'https://api.tacc.utexas.edu/'
    monkeypatch.setenv("_abaco_api_server", client_v2.api_server)
    return


@pytest.fixture()
def abaco_username(monkeypatch, client_v2):
    """Sets value of env variable `_abaco_username`."""
    monkeypatch.setenv("_abaco_username", client_v2.username)
    return


@pytest.fixture()
def abaco_access_token(monkeypatch, token_v2):
    """Sets value of env variable `_abaco_access_token`."""
    monkeypatch.setenv("_abaco_access_token", token_v2)
    return


@pytest.fixture()
def abaco_env(abaco_access_token, abaco_api_server, abaco_username):
    """Invokes upstream fixtures that mock environment vars in the Abaco
    runtime.
    """
    pass