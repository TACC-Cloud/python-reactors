import pytest
import os
import sys

import petname
import re
from reactors.runtime import Reactor
from reactors.runtime.abaco import new_hashid

@pytest.fixture(scope='session')
def fake_version():
    return u'1.0.0'


@pytest.fixture(scope='session')
def fake_alias():
    return petname.Generate(2, '-')


@pytest.fixture(scope='session')
def fake_alias_versioned(fake_alias, fake_version):
    return fake_alias + ':' + fake_version


@pytest.fixture(scope='session')
def fake_alias_prefixed(fake_alias):
    return 'v1-alias-' + fake_alias


@pytest.fixture(scope='session')
def fake_alias_versioned_prefixed(fake_alias_prefixed, fake_version):
    return fake_alias_prefixed + ':' + fake_version


@pytest.fixture(scope='session')
def fake_actor_id():
    return get_id()


@pytest.fixture(scope='session')
def real_actor_id(actor_wc):
    return actor_wc['id']


@pytest.fixture(scope='session')
def tenant_id_url_safe(tenant_id):
    return tenant_id.upper().replace('.', '-')


@pytest.fixture(scope='function')
def r(r_bare):
    return r_bare


def test_add_delete_nonce(r, real_actor_id, tenant_id_url_safe):
    '''Ensure various properties are present and the right class'''
    nonce = r.add_nonce(permission='READ', maxuses=1, actorId=real_actor_id)
    assert 'id' in nonce
    nonce_id = nonce.get('id')
    assert nonce_id
    # Nonces include the tenant ID to allow for routing upstream of APIM
    assert nonce_id.startswith(tenant_id_url_safe)
    deleted = r.delete_nonce(nonce_id, actorId=real_actor_id)
    assert deleted is None


def test_list_nonces(real_actor_id):
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    nonce = r.add_nonce(permission='READ', maxuses=1, actorId=real_actor_id)
    nonce_id = nonce.get('id')
    nonces = r.list_nonces(actorId=real_actor_id)
    assert isinstance(nonces, list)
    count_nonces = len(nonces)
    assert count_nonces >= 1
    r.delete_nonce(nonce_id, actorId=real_actor_id)


def test_create_delete_webhook(real_actor_id, tenant_id_url_safe):
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    webhook_uri = r.create_webhook(actorId=real_actor_id)
    assert tenant_id_url_safe in webhook_uri
    assert real_actor_id in webhook_uri
    r.delete_webhook(webhook_uri, actorId=real_actor_id)


def test_delete_all_nonces(real_actor_id):
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    for a in range(0, 5):
        r.add_nonce(permission='READ', maxuses=1, actorId=real_actor_id)
    nonces = r.list_nonces(actorId=real_actor_id)
    assert isinstance(nonces, list)
    count_nonces = len(nonces)
    assert count_nonces >= 5
    r.delete_all_nonces(actorId=real_actor_id)
    nonces = r.list_nonces(actorId=real_actor_id)
    assert isinstance(nonces, list)
    count_nonces = len(nonces)
    assert count_nonces == 0
