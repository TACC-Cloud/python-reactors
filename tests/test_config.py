import pytest


def test_r_has_attrs(monkeypatch, r, R):
    '''Ensure various properties are present and the right class'''
    assert 'logs' in r.settings.keys()
    assert r.settings.logs.level == 'DEBUG'
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'INFO')
    p = R()
    assert p.settings.logs.level == 'INFO'