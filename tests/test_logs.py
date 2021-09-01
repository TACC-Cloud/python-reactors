import pytest
import os
import sys
<<<<<<< HEAD
=======
import requests
>>>>>>> 21a3dc7db5e0f3f093a0fe6b363ab83c6785f2fe

from reactors.runtime import Reactor


@pytest.fixture(params=['R_tp_opt', 'R_bare'])
def R(request):
    """Tests both fixtures `R_tp_opt` and `R_bare`"""
    return request.getfixturevalue(request.param)


@pytest.fixture(params=['r_tp_opt', 'r_bare'])
def r(request):
    """Tests both fixtures `r_tp_opt` and `r_bare`"""
    return request.getfixturevalue(request.param)


@pytest.mark.tapis_auth
def test_read_logtoken_config(r):
    '''Read the API token for log aggregation from config.yml'''
    assert 'token' in r.settings.logs

<<<<<<< HEAD

@pytest.mark.tapis_auth
def test_read_loggly_config(r):
    '''Read the API token, URL for loggly aggregation from config.yml'''
    assert 'customer_token' in r.settings.loggly
    assert 'url' in r.settings.loggly
=======
# check for loggly customer_token field
@pytest.mark.tapis_auth
def test_read_logglytoken_config(r):
    '''Read the API token for loggly log aggregation from config.yml'''
    assert 'customer_token' in r.settings.loggly

# check if post request to loggly returns 200 OK response
@pytest.mark.tapis_auth
def test_loggly_log(R, caplog, capsys):
    '''Verify logging to Loggly works'''
    message = 'Hello Loggly'
    r = R()
    r.logger.info(message)
    url = r.settings.loggly.url
    customer_token = r.settings.loggly.customer_token
    url = url.replace("{customer_token}", customer_token)
    info_message = {
        'timestamp': 'test',
        'message': 'test log from postman',
        'level': 'INFO'
    }
    response = requests.post(url=url, data=json.dumps(info_message))
    assert response.status_code == 200

>>>>>>> 21a3dc7db5e0f3f093a0fe6b363ab83c6785f2fe


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
<<<<<<< HEAD
    # checking for LOGGLY
    monkeypatch.setenv('_REACTOR_LOGGLY_TOKEN', 'VewyVewySekwittgsEk')
    r = R()
    assert r.settings.logs.token == 'VewyVewySekwit'
    # checking for LOGGLY
    assert r.settings.loggly.token == "VewyVewySekwittgsEk"

# verifying logging to loggly works
@pytest.mark.tapis_auth
def test_log_loggly(R, caplog, capsys):
    '''Verify logging to loggly works'''
    message = 'Hello Loggly'
    r = R()
    r.logger.info(message)
    out, err = capsys.readouterr()
    assert [message] == [rec.message for rec in caplog.records]
    assert message not in out
    assert message in err
=======
    r = R()
    assert r.settings.logs.token == 'VewyVewySekwit'
>>>>>>> 21a3dc7db5e0f3f093a0fe6b363ab83c6785f2fe


@pytest.mark.tapis_auth
def test_log_stderr(R, caplog, capsys):
    '''Verify logging to stderr works'''
    message = 'Hello'
    r = R()
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


@pytest.mark.skip(reason="to be fixed on #34")
@pytest.mark.tapis_auth
@pytest.mark.parametrize('attr_name', [
    'x-nonce',
    'TAPIS_CLI_REGISTRY_PASSWORD'
])
def test_log_redact_attr(R, attr_name, caplog, capsys, monkeypatch):
    '''Verify that certain attributes that usually contain secrets are redacted'''
    message = 'VewyVewySekwit'
    monkeypatch.setenv(attr_name, message)
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = R()
    r.logger.debug('context: {}'.format(r.context))
    out, err = capsys.readouterr()
    assert message not in err
    assert message not in out
    assert message in caplog.text


@pytest.mark.tapis_auth
def test_log_redact_apitoken(R, caplog, capsys, monkeypatch):
    '''Verify that x-nonce is redacted since it is an impersonation token'''
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = R()
    if r.client is None:
        # Tapis optional client
        return
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
