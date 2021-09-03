import pytest
from reactors.logtypes.loggly_futures_session import LogglyHandler
import logging


def test_loggly_handler(R_tp_opt, loggly_token, monkeypatch):
    """Reading Loggly URL from env var, can POST to Loggly using the
    LogglyHandler.
    """
    monkeypatch.setenv('_REACTOR_LOGGLY_CUSTOMER_TOKEN', loggly_token)
    r = R_tp_opt()
    assert isinstance(r.loggers.loggly, logging.Logger), type(r.loggers.loggly)
    lhs = [handler for handler in r.loggers.loggly.handlers 
           if isinstance(handler, LogglyHandler)]
    assert len(lhs) == 1
    lh = lhs[0]
    assert isinstance(lh, LogglyHandler)
    assert not hasattr(lh, '_resp')
    r.loggers.loggly.info('hello from LogglyHandler')
    assert hasattr(lh, '_resp')
    # check the response code from the last emit call
    assert lh._resp.result().status_code == 200
