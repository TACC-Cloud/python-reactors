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
    r.logger.info('Hello from LogglyHandler')
