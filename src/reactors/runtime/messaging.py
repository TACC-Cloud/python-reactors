"""Derived Reactor class implementing inter-actor messages
"""
from agavepy.agave import Agave, AgaveError
from requests.exceptions import HTTPError

from . import abaco, sessions
from .base import BaseReactor


class Messaging(BaseReactor):

    MAX_ELAPSED = 300
    MAX_RETRIES = 5
    RETRY_DELAY = 1.0
    RETRY_MAX_DELAY = 32.0

    def actor_property(self, property=None, actor_id=None):
        """Retrieve an actor property from Abaco API

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

    def resolve_alias(self, alias):
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

        # Implements me/self nickname for the current Actor
        if alias.lower() in ['me', 'self']:
            return self.uid
        
        # If the alias looks like an Abaco hashid, just return it
        if abaco.is_hashid(alias):
            return alias

        # Consult linked_reactors stanza in config.yml. This allows Reactor-
        # scoped override of aliases defined at the service level
        #
        # NOTE - DEPRECATED DO NOT USE
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

        # Because Abaco implements its own alias function,
        # we simply return the name of the alias if it was not
        # processed by any of the above mechanisms
        return alias

    def message_provenance(self, senderTags=True):
        """Captures provenance attributes for current execution
        """
        sender_envs = {}
        if senderTags is True:
            for env in list(abaco.SPECIAL_VARS_MAP.keys()):
                if os.environ.get(env):
                    sender_envs[abaco.SPECIAL_VARS_MAP[env]] = os.environ.get(env)

        if sessions.URL_PARAM not in sender_envs:
            sender_envs[sessions.URL_PARAM] = self.session

        return sender_envs

    def message_vars(self, passed_envs={},
                         sender_envs={}, senderTags=True):
        """
        Private method to merge user- and platform-specific environments
        """
        env_vars = passed_envs
        sender_envs = self.message_provenance(senderTags)
        env_vars.update(sender_envs)
        return env_vars

    # TODO - implement synchronous messaging
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
            senderTags: bool - send provenance and session as urlparams with message
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
            retryMaxAttempts = self.MAX_RETRIES
        if retryDelay is None:
            retryDelay = self.RETRY_DELAY

        # Build dynamic list of variables. This is how attributes like
        # session and sender-id are propagated
        resolved_actor_id = self.resolve_alias(actorId)
        environment_vars = self.message_vars(environment, senderTags)

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
                if retry > RETRY_MAX_DELAY:
                    retry = RETRY_MAX_DELAY

        # Maximum attempts have passed and execution_id was not returned
        if ignoreErrors:
            self.logger.error(terminal_err.format(resolved_actor_id,
                                                  retryMaxAttempts,
                                                  exceptions))
        else:
            raise AgaveError(terminal_err.format(resolved_actor_id,
                                                 retryMaxAttempts,
                                                 exceptions))
