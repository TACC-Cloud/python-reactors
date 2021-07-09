import pytest
from reactors.runtime import Reactor
from collections.abc import Callable



@pytest.fixture
def R_bare() -> type:
    """Returns bare Reactor constructor"""
    return Reactor


@pytest.fixture
def r_bare(R_bare) -> Reactor:
    """Returns bare Reactor instance"""
    return R_bare()


@pytest.fixture
def R(R_bare) -> type:
    return R_bare


@pytest.fixture
def r(r_bare) -> Reactor:
    return r_bare


@pytest.fixture
def R_tp_opt(R_bare) -> type:
    """Returns Reactor constructor, with Tapis optional. Note that the 
    constructor will still attempt to load client using `abaco.load_client`,
    so instances might have active client depending on env.
    """
    R_bare.TAPIS_OPTIONAL = True
    return R_bare


@pytest.fixture
def r_tp_opt(R_tp_opt) -> Reactor:
    """Returns Reactor instance, with Tapis optional. Set NoneType client
    to emulate `load_client(permissive=True)`. 
    """
    r = R_tp_opt()
    r.client = None
    return r