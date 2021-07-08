import pytest
from reactors.runtime import Reactor
from collections.abc import Callable


@pytest.fixture
def r(abaco_env) -> Reactor:
	"""Returns Reactor instance instantiated in Abaco runtime env"""
	return Reactor()


@pytest.fixture
def R(abaco_env) -> type:
	"""Returns Reactor constructor"""
	return Reactor