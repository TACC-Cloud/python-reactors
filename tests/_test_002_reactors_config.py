import pytest
import os
import sys

from reactors.runtime import Reactor


def test_read_default():
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    assert 'logs' in r.settings.keys()


def test_read_override(monkeypatch):
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    assert 'logs' in r.settings.keys()
    assert r.settings.logs.level == 'DEBUG'
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'INFO')
    p = Reactor()
    assert p.settings.logs.level == 'INFO'
