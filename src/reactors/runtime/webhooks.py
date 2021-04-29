"""Derived Reactor class implementing webhooks and nonces
"""
import json
from reactors import agaveutils
from requests.exceptions import HTTPError
from agavepy.errors import AgaveError

from .base import BaseReactor

XNONCE_URL_PARAM = 'x-nonce'
PERMISSIONS = ('READ', 'EXECUTE', 'UPDATE')

class Webhooks(BaseReactor):

    DEFAULT_NONCE_PERMISSION = 'EXECUTE'
    DEFAULT_NONCE_MAX_USES = -1

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
        assert permission in PERMISSIONS, \
            'Invalid permission'
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

    def create_webhook(self, permission=DEFAULT_NONCE_PERMISSION, maxuses=DEFAULT_NONCE_MAX_USES, actorId=None):
        """Create an actor/messages URI for use with external integrations
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
        assert permission in PERMISSIONS, \
            'Invalid permission'
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
