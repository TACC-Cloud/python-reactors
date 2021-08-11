import pytest
from agavepy.agave import AgaveError


@pytest.fixture
def r(r_bare):
    return r_bare


@pytest.mark.tapis_auth
def test_reactors_send_message(r, actor_wc):
    message = 'hello, world'
    # passes when sending to a real actor
    exec_id = r.send_message(actor_wc['id'], message, retryMaxAttempts=1, ignoreErrors=False)
    assert exec_id is not None

    # fails when sending to actor that DNE
    with pytest.raises(AgaveError):
        r.send_message('foobarbaz', message, retryMaxAttempts=1, ignoreErrors=False)
