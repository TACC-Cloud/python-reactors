from __future__ import absolute_import

"""
Utility library for building TACC Reactors
"""

import json
import os
import petname
import re
import sys
import validators
import requests

from time import sleep, time
from random import random

from attrdict import AttrDict
from agavepy.agave import Agave, AgaveError
from agavepy.actors import (get_context, get_client)
# This is the specific error classed raised by AgavePy's HTTP client 
# and it differs from the modern HTTPError
from requests.exceptions import HTTPError

from . import (abaco, agaveutils, jsonmessages, logtypes)
from .config import (parse_boolean, read_config, get_redaction_strings, get_host_ip)

LOG_LEVEL = 'DEBUG'
LOG_FILE = None
HASH_SALT = '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve'
MESSAGE_SCHEMA = '/message.jsonschema'

def get_client_with_mock_support(permissive=False):
    '''
    Get the current Actor API client

    Returns the Abaco actor's client if running deployed. Attempts to
    bootstrap a client from supplied credentials if running in local or
    debug mode.
    '''
    try:
        # The AgavePy method attempts to fail down to Agave.restore()
        return get_client()
    except Exception:
        if permissive is True:
            return None
        else:
            raise

def get_token_with_mock_support(agave_client):
    '''Get current Oauth2 access token from client'''
    try:
        return agave_client.token.token_info['access_token']
    except Exception:
        return None

def get_context_with_mock_support(agave_client):
    '''
    Return the current Actor context

    Return the Abaco actor's environment context if running deployed. Creates
    a mock context based on inferred or mocked values if running in local or
    debug mode.
    '''
    _context = get_context()

    # Detect presence of _abaco_actor_id as a way of 
    actor_id_val = os.environ.get('_abaco_actor_id')
    if actor_id_val is None or actor_id_val == '':
        
        mock_actor_id = abaco.new_hashid()
        mock_exec_id = abaco.new_hashid()
        mock_worker_id = abaco.new_hashid()
        mock_container_name = abaco.new_hashid()
        mock_container_repo = abaco.new_hashid()

        # TODO - look up username if cannot be determined from env
        #        this is the case if only API_URL and TOKEN have been used to set up 
        #        the context
        _username = os.environ.get('_abaco_username')
        if _username is None or _username == '':
            try:
                _username = agave_client.username
            except Exception:
                _username = None

        __context = AttrDict({'raw_message': os.environ.get('MSG', ''),
                              'content_type': 'application/json',
                              'username': _username,
                              'actor_dbid': mock_actor_id,
                              'actor_id': mock_actor_id,
                              'execution_id': mock_exec_id,
                              'worker_id': mock_worker_id,
                              'actor_repo': mock_container_repo,
                              'actor_name': mock_container_name,
                              'state': {}})
        # Merge new values from __context
        _context = _context + __context
        # Update environment
        update_environ(__context, agave_client)

    return AttrDict(_context)

def update_environ(context, agave_client):
    update_environ_with_mock(context)
    update_environ_with_client(agave_client)

def update_environ_with_mock(context):
    '''Set environment vars to values from a context'''
    if context is None:
        context = {}
    try:
        for (env_k, env_v) in context.items():
            abenv = abaco.ABACO_CONTEXT_MAP[env_k]
            os.environ[abenv] = str(env_v)
    except Exception:
        pass
    return True


def update_environ_with_client(agave_client):
    '''Set environment vars to values from an Agave client'''
    try:
        os.environ['_abaco_api_server'] = agave_client.api_server
    except Exception:
        pass
    try:
        os.environ['_abaco_access_token'] = agave_client._token
    except Exception:
        pass
    return True


# def read_config(namespace=NAMESPACE, places_list=CONFIG_LOCS,
#                 update=True, env=True):
#     """Override tacconfig's broken right-favoring merge"""
#     master_config = None
#     for place in places_list:
#         new_config = config.read_config(namespace=namespace,
#                                         places_list=[place],
#                                         env=env)
#         if isinstance(new_config, dict) and master_config is None:
#             master_config = new_config.copy()
#         master_config = master_config + new_config
#     return master_config


def microseconds():
    return int(round(time() * 1000 * 1000))


class Reactor(object):
    """
    Helper class providing a client-side API for the Actors service
    """

    TAPIS_CLIENT_MANDATORY = True
    CONFIG_NAMESPACE = '_REACTOR'
    SEND_MSG_MAX_ELAPSED = 300
    SEND_MSG_MAX_RETRIES = 5
    SEND_MSG_RETRY_DELAY = 1

    def __init__(self,
                 redactions=[], 
                 tapis_client_mandatory=TAPIS_CLIENT_MANDATORY, 
                 namespace=CONFIG_NAMESPACE):

        # Dynamic properties
        self.nickname = petname.Generate(2, '-')
        self.created = microseconds()

        # Inheritied properties

        # Try to get the Agave client, token, etc first
        # These can be None if no client is available. We must
        # be sure to account for that in code that makes API calls
        # TODO - unit test case where client cannot be configured
        self.client = get_client_with_mock_support(permissive=tapis_client_mandatory)
        self._token = get_token_with_mock_support(self.client)
        self.context = get_context_with_mock_support(agave_client=self.client)
        # Set up Tapis API subclient(s)
        if self.client is not None:
            self.pemagent = agaveutils.recursive.PemAgent(self.client)
        else:
            self.pemagent = None

        # Commonly-used properties
        for p, e in [('uid', 'actor_id'), ('execid', 'execution_id'), 
                     ('workerid', 'worker_id'), ('state', 'state'),
                     ('username', 'username'), ('container_repo', 'actor_repo'),
                     ('actor_name', 'actor_name')]:
            setattr(self, p, self.context.get(e))

        # Establish session
        #
        # A session in the Reactors system is a linked set of executions
        # that inherit an identifier from their parent. If a reactor doesn't
        # detect a session on init, it creates one from its nickname. Sessions 
        # are useful for tracing chains or cycles of executions
        # TODO - unit test both env vars and no var at all
        self.session = self.context.get('x_session',
                                        self.context.get(
                                            'SESSION',
                                            self.nickname))

        # The 'local' property can be used by reactor authors to add 
        # conditional behaviors for local usage or testing purposes
        # TODO - unit test some values
        self.local =  parse_boolean(os.environ.get('LOCALONLY'))

        # Load settings dict from env and file via tacconfig
        # Basically: config.yml ** local environment
        self.settings = read_config(update=True, env=True)

        # Set up loggers
        self.loggers = AttrDict({'screen': None, 'slack': None})

        # Strings to redact from all logs
        redact_strings = get_redaction_strings(
            redactions=redactions, agave_client=self.client)

        # Dict of fields that we want to send with each logstash
        # structured log response
        log_fields = {'agent': self.uid,
                      'task': self.execid,
                      'name': self.actor_name,
                      'username': self.username,
                      'session': self.session,
                      'resource': self.container_repo,
                      'subtask': self.workerid,
                      'host_ip': get_host_ip()}

        # Screen logger prints to the following, depending on configuration
        # STDERR - Always
        # FILE   - If log_file is provided
        # AGGREGATOR - If log_token is provided
        self.loggers.screen = logtypes.get_screen_logger(
            self.uid,
            self.execid,
            settings=self.settings,
            redactions=redact_strings,
            fields=log_fields)

        # assuming either env or config.yml is set up
        # correctly, post messages from here to Slack
        self.loggers.slack = logtypes.get_slack_logger(
            self.uid, 'slack', settings=self.settings,
            redactions=redact_strings)

        # Alias to stderr logger so that r.logger continues to work
        self.logger = self.loggers.screen

    def on_success(self, successMessage="Success"):
        """
        Log message and exit 0
        """
        self.logger.info(successMessage)
        sys.exit(0)

    def on_failure(self, failMessage="Failure", exceptionObject=None):
        """
        Log message and exit 0
        """
        self.logger.critical("{} : {}".format(
            failMessage, exceptionObject))
        sys.exit(1)

    def get_actor_property(self, property=None, actor_id=None):
        """Retrieve an actor property

        Parameters:
        property - str - Any top-level key in the Actor API model
        actorId   - str - Which actor (if not self) to fetch. Defaults to
                          the actor's own ID, allowing introspection.
        """

        if actor_id is None:
            fetch_id = self.uid
        else:
            fetch_id = actorId

        try:
            record = self.client.actors.get(actorId=fetch_id)
            if attribute is None:
                return record
            else:
                return record.get(property, None)
        except Exception:
            if actor_id is None and attribute is None:
                return {}
            else:
                return 'mockup'


    def _make_sender_tags(self, senderTags=True):
        """
        Internal function for capturing actor and app provenance attributes
        """
        sender_envs = {}
        if senderTags is True:
            for env in list(abaco.SPECIAL_VARS_MAP.keys()):
                if os.environ.get(env):
                    sender_envs[abaco.SPECIAL_VARS_MAP[env]] = os.environ.get(env)

        if 'x_session' not in sender_envs:
            sender_envs['x_session'] = self.session
        return sender_envs

    def _get_environment(self, passed_envs={},
                         sender_envs={}, senderTags=True):
        """
        Private method to merge user- and platform-specific environments
        """
        env_vars = passed_envs
        sender_envs = self._make_sender_tags(senderTags)
        env_vars.update(sender_envs)
        return env_vars

    def resolve_actor_alias(self, alias):
        """
        Look up the identifier for a alias string

        Arguments
            alias (str): An alias, actorId, appId, or the me/self shortcut

        Returns:
            str: The resolved identifier

        On error:
        Returns value of text

        Note:
            Does basic optimization of returning an app ID or abaco actorId
            if they are passed, as we can safely assume those are not aliases.
        """

        # Implements an internal alias resolving to current Actor
        if alias.lower() in ['me', 'self']:
            return self.uid
        
        # Value that appears to be an Abaco ID rather than an alias
        if abaco.is_hashid(alias):
            return alias

        # No longer supported!
        # if agaveutils.entity.is_appid(alias):
        #     return alias

        # Consult linked_reactors stanza in config.yml. This allows Reactor-
        # scoped override of aliases defined by the Abaco service
        #
        # NOTE - This is DEPRECATED
        try:
            # file:config.yml
            # ---
            # linked_reactors:
            #   <aliasName:str>:
            #       id: <actorId:str>
            #       options: <dict>
            identifier = self.settings.get('linked_reactors', {}).get(alias, {}).get('id', None)
            if identifier is not None and isinstance(identifier, str):
                return identifier
        except KeyError:
            pass

        # Resolution has not failed but rather has identified a value that is
        # likely to be an Abaco platform alias. We do not need to resolve it 
        # to the actual actorID and in fact that is counter-productive since 
        # it will add overhead to whatever process is calling this function
        return alias

    def send_message(self, actorId, message,
                     environment={}, ignoreErrors=True,
                     senderTags=True, retryMaxAttempts=None,
                     retryDelay=None, sync=False):
        """
        Send a message to an Abaco actor by ID or alias

        Arguments:
            actorId (str): An actorId or alias
            message (str/dict) : Message to send

        Keyword Arguments:
            ignoreErrors: bool -  only mark failures by logging not exception
            environment: dict - environment variables to pass as url params
            senderTags: bool - send provenance and session vars along
            retryDelay: int - seconds between retries on send failure
            retryMax: int - number of times (up to global MAX_RETRIES) to retry
            sync: bool - not implemented - wait for message to execute

        Returns:
            str: The executionId of the resulting execution

        Raises:
            AgaveError: Raised if ignoreErrors is True
        """

        # Fail fast
        if self.client is None:
            raise AgaveError('No Tapis client is configured in this Reactor')
        
        # Retry configuration - inherit from class definition
        if retryMaxAttempts is None:
            retryMaxAttempts = self.SEND_MSG_MAX_RETRIES
        if retryDelay is None:
            retryDelay = self.SEND_MSG_RETRY_DELAY

        # Build dynamic list of variables. This is how attributes like
        # session and sender-id are propagated
        resolved_actor_id = self.resolve_actor_alias(actorId)
        environment_vars = self._get_environment(environment, senderTags)

        retry = retryDelay
        attempts = 0
        execution_id = None
        exceptions = []
        noexecid_err = 'Response received from {} but no executionId was found'
        exception_err = 'Exception encountered messaging {}'
        terminal_err = 'Message to {} failed after {} tries with errors: {}'

        self.logger.info("Message.to: {}".format(actorId))
        self.logger.debug("Message.body: {}".format(message))

        while attempts <= retryMaxAttempts:
            try:
                response = self.client.actors.sendMessage(
                    actorId=resolved_actor_id,
                    body={'message': message},
                    environment=environment_vars)

                if 'executionId' in response:
                    execution_id = response.get('executionId')
                    if execution_id is not None:
                        return execution_id
                    else:
                        self.logger.error(
                            noexecid_err.format(resolved_actor_id))
                else:
                    self.logger.error(
                        noexecid_err.format(resolved_actor_id))

            except HTTPError as herr:
                if herr.response.status_code == 404:
                    # Agave never returns 404 unless the thing isn't there
                    # so might as well bail out early if we see one
                    attempts = retryMaxAttempts + 1
                else:
                    http_err_resp = agaveutils.process_agave_httperror(herr)
                    self.logger.error(http_err_resp)

            # This should only happen in egregious circumstances
            # since the vast majority of AgavePy error manifest as
            # a requests HTTPError
            except Exception as e:
                exceptions.append(e)
                self.logger.error(exception_err.format(resolved_actor_id))

            attempts = attempts + 1
            # random-skew exponential backoff with limit
            if attempts <= retryMaxAttempts:
                self.logger.debug('pause {} sec then try again'.format(retry))
                sleep(retry)
                retry = retry * (1.0 + random())
                if retry > 32:
                    retry = 32

        # Maximum attempts have passed and execution_id was not returned
        if ignoreErrors:
            self.logger.error(terminal_err.format(resolved_actor_id,
                                                  retryMaxAttempts,
                                                  exceptions))
        else:
            raise AgaveError(terminal_err.format(resolved_actor_id,
                                                 retryMaxAttempts,
                                                 exceptions))

    def validate_message(self,
                         message,
                         schema=MESSAGE_SCHEMA,
                         permissive=True):
        """
        Validate dictonary derived from JSON against a JSON schema

        Positional arguments:
        message - dict - JSON-derived object

        Keyword arguments:
        schema - str - path to the requisite JSON schema file
        permissive - bool - swallow validation errors [True]
        """
        return jsonmessages.validate_message(message,
                                             schema=schema,
                                             permissive=permissive)

    def create_webhook(self, permission='EXECUTE', maxuses=-1, actorId=None):
        """
        Create a .actor.messages URI suitable for use in integrations

        Default is to grant EXECUTE with unlimited uses.
        """
        if actorId is not None:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            api_server = agaveutils.utils.get_api_server(self.client)
            nonce = self.add_nonce(permission,
                                   maxuses, actorId=_actorId)
            nonce_id = nonce.get('id')
            uri = '{}/actors/v2/{}/messages?x-nonce={}'.format(
                api_server, _actorId, nonce_id)
            if validators.url(uri):
                return uri
            else:
                raise ValueError("Webhook URI {} is not valid".format(uri))
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def delete_webhook(self, webhook, actorId=None):
        """
        'Delete' an actor-specific webhook by deleting its nonce

        A key assumption is that webhook was constructed by create_webhook or
        its equivalent, as this method sensitive to case and url structure
        """
        if actorId is not None:
            _actorId = actorId
        else:
            _actorId = self.uid

        # webhook must be plausibly associated with the specified actor
        if not re.search('/actors/v2/{}'.format(_actorId), webhook):
            raise ValueError("URI doesn't map to actor {}".format(_actorId))

        try:
            m = re.search('x-nonce=([A-Z0-9a-z\\.]+_[A-Z0-9a-z]+)', webhook)
            nonce_id = m.groups(0)[0]
            self.delete_nonce(nonceId=nonce_id, actorId=_actorId)
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def add_nonce(self, permission='READ', maxuses=1, actorId=None):
        """
        Add a new nonce.

        Positional arguments:
        None

        Keyword arguments:
        username: str - a valid TACC.cloud username or role account
        permission: str - a valid Abaco permission level
        maxuses: int (-1,inf) - maximum number of uses for a given nonce
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        assert permission in ('READ', 'EXECUTE', 'UPDATE'), \
            'Invalid permission: (READ, EXECUTE, UPDATE)'
        assert isinstance(maxuses, int), 'Invalid max_uses: (-1,-inf)'
        assert maxuses >= -1, 'Invalid max_uses: (-1,-inf)'
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            body = {'level': permission,
                    'maxUses': maxuses}
            resp = self.client.actors.addNonce(actorId=_actorId,
                                               body=json.dumps(body))
            return resp
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def get_nonce(self, nonceId, actorId=None):
        """
        Get an specific nonce by its ID

        Positional arguments:
        nonceId: str - a valid TACC.cloud username or role account

        Keyword arguments:
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            resp = self.client.actors.getNonce(
                actorId=_actorId, nonceId=nonceId)
            return resp
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def delete_nonce(self, nonceId, actorId=None):
        """
        Delete an specific nonce by its ID

        Positional arguments:
        nonceId: str - a valid TACC.cloud username or role account

        Keyword arguments:
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            resp = self.client.actors.deleteNonce(
                actorId=_actorId, nonceId=nonceId)
            return resp
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def list_nonces(self, actorId=None):
        """
        List all nonces

        Positional arguments:
        None

        Keyword arguments:
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            resp = self.client.actors.listNonces(
                actorId=_actorId)
            return resp
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def delete_all_nonces(self, actorId=None):
        """
        Delete all nonces from an actor

        Keyword arguments:
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            nonces = self.list_nonces(actorId=_actorId)
            assert isinstance(nonces, list)
            for nonce in nonces:
                self.delete_nonce(nonce.get('id'), actorId=_actorId)
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def _get_nonce_vals(self):
        """
        Get nonce value from environment

        Details: Extract value of x-nonce if it was passed. This is used to
        set up redaction, but could also be used to pass the nonce along to
        another context. Currently, we only expect one nonce, but there
        could be nonces from other services so this is implemented to return
        a list of nonce values.
        """
        nonce_vals = []
        try:
            nonce_value = self.context.get('x-nonce', None)
            if nonce_value is not None:
                nonce_vals.append(nonce_value)
        except Exception:
            pass
        return nonce_vals

    def elapsed(self):
        """Returns elapsed time in microseconds since Reactor was initialized"""
        return microseconds() - self.created

# Verified Py3 compatible
