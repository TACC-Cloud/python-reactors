import logging
import pytest
import polling2


def actor_exists(client, body: dict) -> dict:
    for actor in client.actors.list():
        if all(actor[k] == body[k] for k in body):
            logging.debug(f"found match for body with actorId {actor['id']}")
            return actor
    logging.debug(f"no matches for body")
    return dict()


@pytest.fixture
def actor_wc(client_v2):
    """description"""
    body = {
        "image": "abacosamples/wc", 
        "description": "Actor that counts words."
    }

    # try to find registered actor if exists, and add it if it does not
    actor = actor_exists(client_v2, body)
    actor = actor if actor else client_v2.actors.add(body=body)

    # poll until actor's status is READY
    polling2.poll(
        target=lambda: client_v2.actors.get(actorId=actor['id'])['status'], 
        check_success=lambda x: x == 'READY', 
        step=5, 
        timeout=20
    )
