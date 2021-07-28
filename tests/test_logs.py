import pytest
import os
import sys

from reactors.runtime import Reactor


@pytest.fixture
def R(R_bare):
    return R_bare


@pytest.fixture
def r(r_bare):
    return r_bare


@pytest.mark.tapis_auth
def test_read_logtoken_config(r):
    '''Read the API token for log aggregation from config.yml'''
    assert 'token' in r.settings.logs


@pytest.mark.tapis_auth
def test_non_null_config_settings(r):
    """No items in Reactor.settings.logger are null. For documentation purposes
    """
    for item in r.settings.logger.items():
        assert item is not None


@pytest.mark.tapis_auth
def test_read_logtoken_env(R, monkeypatch):
    '''Read the API token for log aggregation from environment'''
    monkeypatch.setenv('_REACTOR_LOGS_TOKEN', 'VewyVewySekwit')
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = R()
    assert r.settings.logs.token == 'VewyVewySekwit'


@pytest.mark.tapis_auth
def test_log_stderr(r, caplog, capsys):
    '''Verify logging to stderr works'''
    message = 'Hello'
    r.logger.info(message)
    out, err = capsys.readouterr()
    assert [message] == [rec.message for rec in caplog.records]
    assert message not in out
    assert message in err


# def test_logger_logfile(monkeypatch):
#     '''Verify that message is written to a file'''
#     monkeypatch.setenv('_REACTOR_LOGS_FILE', 'testing.log')
#     monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
#     message = 'Hola'
#     r = Reactor()
#     r.logger.info(message)
#     file = open('testing.log', 'r')
#     assert message in file.read()
#     os.remove('testing.log')

@pytest.mark.tapis_auth
@pytest.mark.parametrize('env_name', [
    '_REACTOR_LOGS_TOKEN',
    '_REACTOR_LOGGER_CLIENT_KEY'
])
def test_log_redact_env(R, env_name, caplog, capsys, monkeypatch):
    '''Verify that the text of an override value cannot be logged'''
    monkeypatch.setenv('_REACTOR_REDACT', 'VewyVewySekwit')
    monkeypatch.setenv(env_name, 'VewyVewySekwit')
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = R()
    r.logger.debug(r.settings)
    out, err = capsys.readouterr()
    assert 'VewyVewySekwit' not in err
    assert 'VewyVewySekwit' not in out
    assert 'VewyVewySekwit' in caplog.text


@pytest.mark.tapis_auth
def test_log_redact_nonce(R, caplog, capsys, monkeypatch):
    '''Verify that x-nonce is redacted since it is an impersonation token'''
    message = 'VewyVewySekwit'
    monkeypatch.setenv('x-nonce', message)
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = R()
    r.logger.debug('context: {}'.format(r.context))
    out, err = capsys.readouterr()
    assert message not in err
    assert message in caplog.text


@pytest.mark.tapis_auth
def test_log_redact_apitoken(R, caplog, capsys, monkeypatch):
    '''Verify that x-nonce is redacted since it is an impersonation token'''
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = R()
    message = r.client._token
    r.logger.debug('redact this token: {}'.format(message))
    out, err = capsys.readouterr()
    assert message not in err
    assert message in caplog.text


@pytest.mark.tapis_auth
def test_log_redact_inited(R, caplog, capsys, monkeypatch):
    '''Verify that content of 'redactions' list passed to init() are honored'''
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    message = 'Sekwit'
    r = R(redactions=[message])
    r.logger.debug('I have a Very{}Message for you!'.format(message))
    out, err = capsys.readouterr()
    assert message not in err
    assert message in caplog.text
