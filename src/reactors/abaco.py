"""Abaco-related vars and helper functions
"""
import uuid
from hashids import Hashids

# This is the salt that Abaco uses when creating 
# actor, execution, nonce, and worker identifiers. It 
# can be used to soft-check the validity of a string 
# presented as an Abaco unique identifier
#
# Ref: https://github.com/TACC/abaco/blob/7165a831ec81521e164b770eba6cccf17e48642b/actors/models.py#L27
HASH_SALT = 'eJa5wZlEX4eWU'

__all__ = ['SPECIAL_VARS_MAP', 'ABACO_CONTEXT_MAP', 'new_hashid', 'is_hashid']

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
    """
    Generate a valid Abaco-style hash id
    """
    hashids = Hashids(salt=HASH_SALT)
    _uuid = uuid.uuid1().int >> 64
    return hashids.encode(_uuid)


def is_hashid(identifier):
    """
    Tries to validate a string presented as an Abaco identifier
    """
    hashids = Hashids(salt=HASH_SALT)
    dec = hashids.decode(identifier)
    if len(dec) > 0:
        return True
    else:
        return False

