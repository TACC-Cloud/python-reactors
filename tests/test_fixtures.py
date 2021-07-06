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
