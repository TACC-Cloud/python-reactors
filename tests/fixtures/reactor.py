import pytest
from reactors.runtime import Reactor
from collections.abc import Callable


@pytest.fixture
def r() -> Reactor:
	"""Returns Reactor instance"""
	return Reactor()


@pytest.fixture
def R() -> type:
	"""Returns Reactor constructor"""
	return Reactor