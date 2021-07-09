import pytest


@pytest.fixture
def R(R_tp_opt):
    return R_tp_opt


# @pytest.mark.tapis_auth
def test_r_has_attrs(monkeypatch, R):
    '''Ensure various properties are present and the right class'''
    r = R()
    assert 'logs' in r.settings.keys()
    assert r.settings.logs.level == 'DEBUG'
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'INFO')
    p = R()
    assert p.settings.logs.level == 'INFO'