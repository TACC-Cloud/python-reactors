import pytest
from reactors.logtypes.loggly_futures_session import LogglyHandler
import logging


def test_token_from_env(R_tp_opt, monkeypatch):
    """Check that Loggly token in environment is valid."""
    monkeypatch.setenv('_REACTOR_LOGGLY_CUSTOMER_TOKEN', 'VewyVewySekwit')
    r = R_tp_opt()
    assert r.settings.loggly.customer_token == 'VewyVewySekwit'


def test_url_from_env(R_tp_opt, monkeypatch):
    """Check that Loggly token in environment is valid."""
    monkeypatch.setenv('_REACTOR_LOGGLY_URL', 'VewyVewySekwit')
    r = R_tp_opt()
    assert r.settings.loggly.url == 'VewyVewySekwit'


def test_loggly_handler(R_tp_opt, loggly_url, monkeypatch):
    """Reading Loggly URL from env var, can POST to Loggly using the
    LogglyHandler.
    """
    monkeypatch.setenv('_REACTOR_LOGGLY_URL', loggly_url)
    r = R_tp_opt()
    r.logger.info('hello from LogglyHandler')


def test_loggly_handler_raises(R_tp_opt, loggly_url, monkeypatch):
    """Reading Loggly URL from env var, can POST to Loggly using the
    LogglyHandler.
    """

    def emit_response_hook(resp, *args, **kwargs):
        assert 0


    monkeypatch.setenv('_REACTOR_LOGGLY_URL', 'bogus_url')
    r = R_tp_opt()
    assert isinstance(r.loggers.loggly, logging.Logger), type(r.loggers.loggly)
    lhs = [
        handler for handler in r.loggers.loggly.handlers 
        if isinstance(handler, LogglyHandler) 
    ]
    assert len(lhs) == 1
    lh = lhs[0]
    assert isinstance(lh, LogglyHandler)
    assert hasattr(lh, 'RAISE_ERRORS')
    lh.RAISE_ERRORS = True
    lh.EMIT_RESPONSE_HOOK = emit_response_hook


    r.loggers.loggly.info('hello from LogglyHandler')
