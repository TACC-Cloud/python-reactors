import pytest
import os
import sys

from agavepy.agave import AgaveError
from reactors.utils import Reactor

@pytest.mark.skip
@pytest.mark.parametrize("actor_id, message, success", [
    ('4xvmNVBxeEDRN', {'text': '4xvmNVBxeEDRN'}, True),
    # ('sd2eadm-listener', {'text': 'sd2eadm-listener'}, True),
    ('meep-meep-meep', {'text': 'meep-meep-meep'}, False)])
def test_reactors_send_message(actor_id, message, success):
    r = Reactor()
    if success is True:
        exec_id = r.send_message(actor_id, message, retryMaxAttempts=1, ignoreErrors=False)
        assert exec_id is not None
    else:
        with pytest.raises(AgaveError):
            r.send_message(actor_id, message, retryMaxAttempts=1, ignoreErrors=False)
