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

    def __init__(self, url):
        super(LogglyHandler, self).__init__()
        self.url = url
    
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

        if post_url is not None:
            try:
                # As per https://github.com/ross/requests-futures#working-in-the-background
                self._resp = session.post(
                    post_url, json=log_entry, headers=headers, 
                    hooks={'response': response_hook_noop})
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                self.handleError(record)
        else:
            pass
