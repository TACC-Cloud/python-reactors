"""Abaco-related vars and helper functions
"""
import copy
import os
import uuid

from agavepy.actors import get_client, get_context
from attrdict import AttrDict
from hashids import Hashids

# This is the salt that Abaco uses when creating 
# actor, execution, nonce, and worker identifiers. It 
# can be used to soft-check the validity of a string 
# presented as an Abaco unique identifier
#
# Ref: https://github.com/TACC/abaco/blob/7165a831ec81521e164b770eba6cccf17e48642b/actors/models.py#L27
HASH_SALT = 'eJa5wZlEX4eWU'

# Mapping between environment variable and parameters to pass along to child messages
SPECIAL_VARS_MAP = {'_abaco_actor_id': 'x_src_actor_id',
                    '_abaco_execution_id': 'x_src_execution_id',
                    'APP_ID': 'x_src_app_id',
                    'JOB_ID': 'x_src_job_id',
                    'EVENT': 'x_src_event',
                    'UUID': 'x_src_uuid',
                    '_event_uuid': 'x_session'}

# Mapping between Abaco context names and underlying environment variables
ABACO_CONTEXT_MAP = {'content_type': '_abaco_Content-Type',
                     'execution_id': '_abaco_execution_id',
                     'username': '_abaco_username',
                     'state': '_abaco_actor_state',
                     'actor_dbid': '_abaco_actor_dbid',
                     'actor_id': '_abaco_actor_id',
                     'raw_message': 'MSG'}


def new_hashid():
    """Generates a valid Abaco-style hash id
    """
    hashids = Hashids(salt=HASH_SALT)
    _uuid = uuid.uuid1().int >> 64
    return hashids.encode(_uuid)


def is_hashid(identifier):
    """Validates a string presented as an Abaco identifier
    """
    hashids = Hashids(salt=HASH_SALT)
    dec = hashids.decode(identifier)
    if len(dec) > 0:
        return True
    else:
        return False


def load_context(enable_mocks=True):
    # Replaces the byzantine get_context_with_mock_support
    # which predates the inbuilt capabilities of AgavePy to 
    # bootstrap from environment variables. A current side 
    # effect of this implementation is that the mocked
    # context is not *exactly* the same as a real context
    # It is missing the 

    # Diagnose whether we are running under Abaco
    actor_id_val = os.environ.get('_abaco_actor_id')
    if actor_id_val is not None and actor_id_val != '':
        return AttrDict(get_context())
    else:
        if enable_mocks:
            # Build a mock context
            ab_ctxt = get_context()
            ctxt = {'raw_message': os.environ.get('MSG', ''),
                    'username': os.environ.get('USER', 'reactor'),
                    'content_type': 'application/json',
                    'actor_dbid': new_hashid(),
                    'actor_id': new_hashid(),
                    'execution_id': new_hashid(),
                    'worker_id': new_hashid(),
                    'actor_repo': new_hashid(),
                    'actor_name': new_hashid(),
                    'state': {}}

            # Merge in mock values if not provided by Abaco context
            merged_ctxt = ab_ctxt
            for k, v in ctxt.items():
                if ab_ctxt.get(k, None) is not None:
                    merged_ctxt[k] = ab_ctxt.get(k)
                else:
                    merged_ctxt[k] = v

            return AttrDict(merged_ctxt)
        else:
            # TODO - raise a more specific exception
            raise Exception("Unable to load Reactor context from environment (or return a mock value)")

def load_client(permissive=False):
    """Gets the current Tapis API client

    Returns the Abaco actor's client if running deployed. Attempts to
    bootstrap a client from supplied credentials if running in local or
    debug mode.
    """
    # Resolution order (agavepy.actors#getclient)
    #
    # 1. Abaco context variables
    # 2. Values from TAPIS_BASE_URL + TAPIS_TOKEN
    # 3. Cache from ~/.agave/current
    try:
        return get_client()
    except Exception:
        if permissive is True:
            return None
        else:
            raise

