"""Manages configuration from environment and files
"""
import datetime
import os

from tacconfig import config as tacconfig

NAMESPACE = 'TACC'
HERE = os.path.dirname(os.path.abspath(__file__))
# Search path for config.yml is root, module path, pwd
CONFIG_LOCS = ['/', HERE, os.getcwd()]

__all__ = ['parse_boolean', 'read_config', 'get_redaction_strings']

def parse_boolean(s):
    """Parse values of Python basic types into equivalent Boolean."""
        
    if isinstance(s, bool):
        return s
    elif s is None:
        return False
    elif isinstance(s, (int, float)):
        return bool(s)
    elif isinstance(s, str):
        BOOLEAN_TRUE_STRINGS = ('t', 'true', 'on', 'ok', 'y', 'yes', '1')
        BOOLEAN_FALSE_STRINGS = ('f', 'false', 'off', 'n', 'no', '0', '')
        s = s.strip().lower()
        if s in BOOLEAN_TRUE_STRINGS:
            return True
        elif s in BOOLEAN_FALSE_STRINGS:
            return False
        else:
            raise ValueError('Invalid boolean value string %r' % s)
    else:
        raise TypeError('Cannot parse input with type {}'.format(type(s)))

def int_or_none(value):
    if value is None:
        return value
    return int(value)

def array_from_string(s):
    array = s.split(',')
    if "" in array:
        array.remove("")
    return array


def set_from_string(s):
    return set(array_from_string(s))

def read_config(namespace=None, places_list=None,
                update=True, env=True):

    """Override tacconfig's broken right-favoring merge"""
    if namespace is None:
        namespace = NAMESPACE
    if places_list is None:
        places_list = CONFIG_LOCS
    
    merged_config = None

    # Override tacconfig's broken right-favoring merge
    for place in places_list:
        new_config = tacconfig.read_config(
            namespace=namespace,
            places_list=[place],
            env=env)
        if isinstance(new_config, dict) and merged_config is None:
            merged_config = new_config.copy()
        merged_config = merged_config + new_config
    
    return merged_config

def get_redaction_strings(redactions=None, agave_client=None, namespace=None):

        # We start with specified redactions, add Tapis-specific sensitive 
        # values, then append values of any variables passed via the 
        # tacconfig environment variable override system. The assumption is that
        # all these values are probably sensitive (or secret) and
        # should not be discoverable on logs

        envstrings = []

        if redactions is None:
            redactions = []

        if namespace is None:
            namespace = NAMESPACE

        # Start with user-provided redactions        
        if len(redactions) > 0 and isinstance(redactions, list):
            envstrings = redactions
        
        # Fetch the current Oauth access token
        try:
            if len(agave_client._token) > 3:
                envstrings.append(agave_client._token)
        except Exception:
            pass

        # Redact the Nonce if there is one
        try:
            nonce = os.environ.get('x-nonce')
            if nonce is not None and nonce != '':
                envstrings.extend(nonce)
        except Exception:
            pass

        # Redact taccconfig environment overrides
        try:
            env_config_vals = tacconfig.get_env_config_vals(namespace=namespace)
            envstrings.extend(env_config_vals)
        except Exception:
            pass

        # De-duplicate
        envstrings = list(set(envstrings))

        return envstrings
