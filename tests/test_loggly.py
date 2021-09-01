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
