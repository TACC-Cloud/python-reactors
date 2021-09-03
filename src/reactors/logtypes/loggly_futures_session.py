import json
import logging
import logging.handlers
import traceback

import requests
from requests_futures.sessions import FuturesSession

# Adapted from https://github.com/loggly/loggly-python-handler/blob/master/loggly/handlers.py

session = FuturesSession()


def bg_cb(sess, resp):
    """Noop the response so logging is fire-and-forget"""
    pass


# As per https://github.com/ross/requests-futures#working-in-the-background


def response_hook_noop(resp, *args, **kwargs):
    """Noop the response so logging is fire-and-forget
    """
    pass



class LogglyHandler(logging.Handler):
    """Send logs to Loggly HTTPS handler"""
    EMIT_RESPONSE_HOOK = response_hook_noop
    RAISE_ERRORS = False

    def __init__(self, config):
        if not isinstance(config, dict):
            config = {}
        # https://logs-01.loggly.com/inputs/{customer_token}/tag/python
        # replace the {customer_token} with the real token here.

        url = config.get('url')
        customer_token = config.get('customer_token')
        if url is None:
            self.url = str()
        else:
            self.url = url
        if customer_token is None:
            self.customer_token = str()
        else:
            self.customer_token = customer_token

        self.url = self.url.replace("{customer_token}", self.customer_token)
        super(LogglyHandler, self).__init__()

    def get_full_message(self, record):
        if record.exc_info:
            return '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            return record.getMessage()

    def emit(self, record):

        post_url = self.url
        fmted = self.format(record)

        try:
            log_entry = json.loads(fmted)
        except Exception:
            log_entry = fmted

        headers = {'Content-type': 'application/json'}

        assert 0
        if post_url is not None:
            try:
                # As per https://github.com/ross/requests-futures#working-in-the-background
                resp = session.post(post_url, json=log_entry,
                             headers=headers,
                             hooks={'response': self.EMIT_RESPONSE_HOOK})
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                if self.RAISE_ERRORS:
                    raise
                self.handleError(record)
        else:
            pass
