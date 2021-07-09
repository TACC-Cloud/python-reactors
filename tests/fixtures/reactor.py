import pytest
import functools
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
def R_tp_opt(R_bare) -> type:
    """Returns Reactor subclass type, with Tapis optional and a constructor
    that sets `client` to NoneType. This emulates an env with no Tapis
    auth available, EXCEPT within the Reactor.__init__ method.
    """
    class R_tp_opt(R_bare):
        TAPIS_OPTIONAL = True

        def __init__(self, *args, **kwargs):
            super(R_tp_opt, self).__init__(*args, **kwargs)
            self.client = None
        
    return R_tp_opt


@pytest.fixture
def r_tp_opt(R_tp_opt) -> Reactor:
    """Returns Reactor instance, with Tapis optional. Set NoneType client
    to emulate `load_client(permissive=True)`. 
    """
    return R_tp_opt()