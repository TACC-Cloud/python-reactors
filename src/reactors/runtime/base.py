"""Reactor base class
"""
import os
import sys

import petname
from attrdict import AttrDict
from .. import agaveutils, logtypes
from ..config import get_redaction_strings, parse_boolean, read_config
from ..utils import get_host_ip, microseconds
from . import abaco, sessions


class BaseReactor(object):

    CONFIG_NAMESPACE = '_REACTOR'
    EXIT_CODE = 1
    MOCK_ENABLED = True
    NICKNAME_WORDS = 2
    NICKNAME_SEP = '-'
    TAPIS_OPTIONAL = False

    def __init__(self, redactions=[], namespace=CONFIG_NAMESPACE, session=None, tapis_optional=TAPIS_OPTIONAL, **kwargs):

        # Timestamp
        self.created = microseconds()

        # Tapis client
        self.client = abaco.load_client(permissive=tapis_optional)
        # Load context, from which we can load client and other bits
        self.context = abaco.load_context(enable_mocks=self.MOCK_ENABLED)
        # Message
        self.message = self.context.get('message_dict')
        # TODO - actually implement this
        self.binary = None

        # Set nickname and session
        #
        # A session in the Reactors SDK is a linked set of executions
        # that inherit an identifier from their parent. If a reactor doesn't
        # detect a session on init, it creates one from its nickname. Sessions
        # are useful for tracing chains or cycles of executions
        #
        # The SDK honors two variables: x_session and SESSION. It is also
        # possible to explicitly set 'session' when initializing a Reactor object
        #
        if session is not None and isinstance(session, str):
            self.session = session
            self.nickname = self.session
        else:
            self.nickname  = petname.Generate(self.NICKNAME_WORDS, self.NICKNAME_SEP)
            self.session = sessions.get_session(self.context, self.nickname)

        # Basic properties(property name, context var)
        for pn, cv in [('uid', 'actor_id'), ('execid', 'execution_id'),
                     ('workerid', 'worker_id'), ('state', 'state'),
                     ('username', 'username'), ('container_repo', 'actor_repo'),
                     ('actor_name', 'actor_name')]:
            setattr(self, pn, self.context.get(cv))

        # The 'local' property can be used by Reactor authors to add
        # conditional behaviors for local usage or testing purposes
        self.local =  parse_boolean(os.environ.get('LOCALONLY'))

        # Set up Tapis API subclient(s)
        if self.client is not None:
            self.pemagent = agaveutils.recursive.PemAgent(self.client)
        else:
            self.pemagent = None

        # Load settings dict from env and file via tacconfig
        # Result: config.yml ** local environment
        self.settings = read_config(update=True, env=True, namespace=namespace)

        # Initialize logging
        self.loggers = AttrDict({'screen': None, 'slack': None, "loggly": None})

        # Fields to send with each structured log response
        log_fields = {'agent': self.uid,
                      'task': self.execid,
                      'name': self.actor_name,
                      'username': self.username,
                      'session': self.session,
                      'resource': self.container_repo,
                      'subtask': self.workerid,
                      'host_ip': get_host_ip()}

        # Build a list of strings to redact from logs
        #
        # This includes user-defined strings, variables passed to override
        # config.yml, and current Tapis secrets
        redact_strings = get_redaction_strings(
            redactions=redactions, agave_client=self.client, namespace=namespace)

        # Posts to these locations depending on configuration
        # STDERR - Always
        # FILE   - If log_file is provided
        # AGGREGATOR - If log_token is provided
        self.loggers.screen = logtypes.get_screen_logger(
            self.uid,
            self.execid,
            settings=self.settings,
            redactions=redact_strings,
            fields=log_fields)

        # Post plaintext logs to Slack (if configured with a webhook)
        self.loggers.slack = logtypes.get_slack_logger(
            self.uid, 'slack', settings=self.settings,
            redactions=redact_strings)

        # # Post logs to Loggly
        self.loggers.loggly = logtypes.get_loggly_logger(
            self.uid, 'loggly', settings=self.settings,
            redactions=redact_strings, fields=log_fields)

        # Alias that allows r.logger to continue working
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
        sys.exit(self.EXIT_CODE)

    def elapsed(self):
        """Returns elapsed time in microseconds since Reactor was initialized"""
        return microseconds() - self.created
