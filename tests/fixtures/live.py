import logging
import pytest
import polling2
import requests
from collections.abc import Mapping, Iterable


def entity_exists(body: Mapping, entities: Iterable) -> dict:
    """Check if all items in `body` match items in any element of `entities`.
    Returns first match as a dict, or an empty dict if no match is found.
    """
    for entity in entities:
        if all(entity[k] == body[k] for k in body):
            return entity
    return dict()


def actor_exists(client, body: Mapping) -> dict:
    return entity_exists(body, client.actors.list())


def app_exists(client, body: Mapping) -> dict:
    return entity_exists(body, client.apps.list())


@pytest.fixture(scope='session')
def actor_wc(client_v2) -> dict:
    """Deploys a word count actor if one does not already exist.
    TODO: consider adding a teardown routine
    """
    body = {
        "image": "abacosamples/wc", 
        "description": "Actor that counts words."
    }

    # try to find registered actor if exists, and add it if it does not
    actor = actor_exists(client_v2, body)
    if actor:
        logging.debug(f"actor with body '{body}' already exists (ID={actor['id']}")
    else:
        logging.debug(f"adding new actor with body '{body}'...")
        actor = client_v2.actors.add(body=body)

    # poll until actor's status is READY
    resp = polling2.poll(
        target=lambda: client_v2.actors.get(actorId=actor['id']), 
        check_success=lambda x: x['status'] == 'READY', 
        ignore_exceptions=(requests.exceptions.ConnectionError,),
        step=5, 
        timeout=20
    )
    yield resp

    # delete all nonces for this actor
    nonces = client_v2.actors.listNonces(actorId=actor['id'])
    assert isinstance(nonces, list)
    logging.debug(f"deleting all nonces for fixture actor {actor['id']}")
    for nonce in nonces:
        client_v2.actors.deleteNonce(nonceId=nonce.get('id'), actorId=actor['id'])


@pytest.fixture(scope='session')
def execution_system(client_v2) -> dict:
    """Creates a private executions system"""
    raise NotImplementedError()


@pytest.fixture(scope='session')
def storage_system(client_v2) -> dict:
    """Creates a private storage system"""
    raise NotImplementedError()


@pytest.fixture(scope='session')
def file(client_v2, storage_system) -> dict:
    """Deploys a live app if one does not already exist."""
    raise NotImplementedError("requires an executionSystem")


@pytest.fixture(scope='session')
def app(client_v2, execution_system) -> dict:
    """Deploys a live app if one does not already exist."""
    raise NotImplementedError("requires an executionSystem")