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


@pytest.mark.tp_auth
def test_add_list_delete_nonce(r, real_actor_id, tenant_id_url_safe):
    '''Create a nonce for an upstream actor, list it, and delete it.'''
    # can add
    nonce = r.add_nonce(permission='READ', maxuses=1, actorId=real_actor_id)
    assert 'id' in nonce

    # can get 
    nonce_id = nonce.get('id')
    assert nonce_id
    
    # can list 
    nonces = r.list_nonces(actorId=real_actor_id)
    assert isinstance(nonces, list)
    count_nonces = len(nonces)
    assert count_nonces >= 1

    # can delete
    # Nonces include the tenant ID to allow for routing upstream of APIM
    assert nonce_id.startswith(tenant_id_url_safe)
    deleted = r.delete_nonce(nonce_id, actorId=real_actor_id)
    assert deleted is None


@pytest.mark.tp_auth
def test_create_delete_webhook(r, real_actor_id, tenant_id_url_safe):
    '''Can create and delte webhook for an upstream actor'''
    webhook_uri = r.create_webhook(actorId=real_actor_id)
    assert tenant_id_url_safe in webhook_uri
    assert real_actor_id in webhook_uri
    r.delete_webhook(webhook_uri, actorId=real_actor_id)


@pytest.mark.tp_auth
def test_delete_all_nonces(r, real_actor_id):
    '''Can delete all nonces for a live actor'''
    for a in range(5):
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
