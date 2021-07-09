import pytest
from reactors.runtime import Reactor
from collections.abc import Callable


@pytest.fixture
def R() -> type:
    """Returns Reactor constructor"""
    return Reactor


@pytest.fixture
def r(R) -> Reactor:
    """Returns Reactor instance"""
    return R()


@pytest.fixture
def R_tp_opt(R) -> type:
    """Returns Reactor constructor, with Tapis optional. Note that the 
    constructor will still attempt to load client using `abaco.load_client`,
    so instances might have active client depending on env.
    """
    R.TAPIS_OPTIONAL = True
    return R


@pytest.fixture
def r_tp_opt(R_tp_opt) -> Reactor:
    """Returns Reactor instance, with Tapis optional. Set NoneType client
    to emulate `load_client(permissive=True)`. 
    """
    r = R_tp_opt()
    r.client = None
    return r