import pytest
import os
import sys

from attrdict import AttrDict
from agavepy.agave import Agave
from logging import Logger

from reactors.runtime import Reactor
from reactors.runtime.abaco import ABACO_CONTEXT_MAP

def test_init():
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    assert r.uid is not None
    assert r.execid is not None
    assert r.state is not None
    assert isinstance(r.local, bool)
    assert isinstance(r.context, AttrDict)
    # assert isinstance(r.state, dict)
    assert isinstance(r.client, Agave)
    assert isinstance(r.logger, Logger)


def test_localonly_true_1(monkeypatch):
    '''Check LOCALONLY x Reactor.local set -> True'''
    monkeypatch.setenv('LOCALONLY', '1')
    r = Reactor()
    rlocal = r.local
    assert rlocal is True

def test_localonly_true_yes(monkeypatch):
    '''Check LOCALONLY x Reactor.local set -> True'''
    monkeypatch.setenv('LOCALONLY', 'yes')
    r = Reactor()
    rlocal = r.local
    assert rlocal is True

def test_localonly_false_empty(monkeypatch):
    '''Check LOCALONLY x Reactor.local unset -> False'''
    monkeypatch.setenv('LOCALONLY', '')
    r = Reactor()
    rlocal = r.local
    assert rlocal is False

def test_localonly_false_0(monkeypatch):
    '''Check LOCALONLY x Reactor.local unset -> False'''
    monkeypatch.setenv('LOCALONLY', '0')
    r = Reactor()
    rlocal = r.local
    assert rlocal is False

def test_localonly_false_no(monkeypatch):
    '''Check LOCALONLY x Reactor.local unset -> False'''
    monkeypatch.setenv('LOCALONLY', 'no')
    r = Reactor()
    rlocal = r.local
    assert rlocal is False

def test_username_from_env(monkeypatch):
    '''Can we pick up username from ENV'''
    monkeypatch.setenv('_abaco_username', 'taco')
    assert '_abaco_username' in os.environ
    r = Reactor()
    assert 'username' in r.context
    r_uname = r.username
    assert r_uname == 'taco'


def test_username_from_client():
    '''Can we pick up username from Agave.client'''
    from agavepy.agave import Agave
    ag = Agave.restore()
    local_uname = ag.profiles.get()['username']
    r = Reactor()
    assert local_uname == r.username


def test_token_available():
    '''Can we pick up Oauth token'''
    r = Reactor()
    assert r._token is not None
    assert isinstance(r._token, str)


def test_x_session(monkeypatch):
    '''can we get x_session from environment'''
    monkeypatch.setenv('x_session', 'smooth-eel')
    r = Reactor()
    assert r.session == 'smooth-eel'


def test_session(monkeypatch):
    '''can we get SESSION from environment'''
    monkeypatch.setenv('SESSION', 'slimy-eel')
    r = Reactor()
    assert r.session == 'slimy-eel'


def test_session_env(monkeypatch):
    '''can we set up environment for messaging'''
    monkeypatch.setenv('SESSION', 'slimy-eel')
    r = Reactor()
    e = r._get_environment()
    assert isinstance(e, dict)
    assert 'x_session' in e
    assert e['x_session'] == 'slimy-eel'


def test_session_autoname(monkeypatch):
    '''can we bootstrap a session name'''
    monkeypatch.setenv('nickname', 'slimy-eel')
    r = Reactor()
    assert r.nickname == r.session


def test_env_from_mock():
    '''Does the environment get populated in mock context'''
    r = Reactor()
    tok = r.client._token
    srv = r.client.api_server
    assert os.environ.get('_abaco_api_server', None) == srv
    assert os.environ.get('_abaco_access_token', None) == tok
    for k, v in ABACO_CONTEXT_MAP.items():
        assert v in os.environ.keys()
