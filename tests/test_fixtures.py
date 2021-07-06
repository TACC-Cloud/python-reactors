import os
import pytest
from agavepy.agave import Agave


def test_client_v2(client_v2):
	"""Test fixture `client_v2`"""
	assert isinstance(client_v2, Agave)
	_ = client_v2.apps.list()


def test_token_v2(token_v2):
	"""Test fixture `token_v2`"""
	assert isinstance(token_v2, str)
	assert token_v2


def test_abaco_username(abaco_username):
    """Test fixture `abaco_username`"""
    assert abaco_username is None
    assert '_abaco_username' in os.environ


def test_abaco_api_server(abaco_api_server):
    """Test fixture `abaco_api_server`"""
    assert abaco_api_server is None
    assert '_abaco_api_server' in os.environ


def test_abaco_access_token(abaco_access_token):
    """Test fixture `abaco_access_token`"""
    assert abaco_access_token is None
    assert '_abaco_access_token' in os.environ
