from typing import MappingView
import pytest
from pathlib import Path
from agavepy.agave import Agave


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
def abaco_api_server(monkeypatch):
	"""Sets value of env variable `_abaco_api_server`."""
	api_server = 'https://api.tacc.utexas.edu/'
	monkeypatch.setenv("_abaco_api_server", api_server)
	yield
	monkeypatch.delenv("_abaco_api_server")


@pytest.fixture()
def abaco_username(monkeypatch):
	"""Sets value of env variable `_abaco_username`."""
	username = 'eho'
	monkeypatch.setenv("_abaco_username", username)
	yield
	monkeypatch.delenv("_abaco_username")

@pytest.fixture()
def abaco_access_token(monkeypatch):
	"""Sets value of env variable `_abaco_access_token`."""
	token = ''
	monkeypatch.setenv("_abaco_access_token", token)
	yield
	monkeypatch.delenv("_abaco_access_token")