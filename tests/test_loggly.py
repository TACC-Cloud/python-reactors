import pytest
from reactors.logtypes.loggly_futures_session import LogglyHandler
import logging


def test_loggly_handler(R_tp_opt, loggly_token, monkeypatch):
    """Reading Loggly customer token from env var, can POST to Loggly using the
    LogglyHandler.
    """
    monkeypatch.setenv('_REACTOR_LOGGLY_CUSTOMER_TOKEN', loggly_token)
    r = R_tp_opt()

    # get the LogglyHandler instance
    assert isinstance(r.loggers.loggly, logging.Logger), type(r.loggers.loggly)
    lhs = [handler for handler in r.loggers.loggly.handlers 
           if isinstance(handler, LogglyHandler)]
    assert len(lhs) == 1
    lh = lhs[0]
    assert isinstance(lh, LogglyHandler)

    # try posting and check the status code
    assert not hasattr(lh, '_resp')
    r.loggers.loggly.info('hello from LogglyHandler')
    assert hasattr(lh, '_resp')
    assert lh._resp.result().status_code == 200

    # now bork the token and check that the response fails to POST
    bogus_token = "bogus_token"
    lh.url = 'https://logs-01.loggly.com/inputs/{}/tag/python'.format(bogus_token)
    r.loggers.loggly.info('this message from LogglyHandler wont go through')
    assert lh._resp.result().status_code != 200

