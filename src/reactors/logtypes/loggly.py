import json
import logging
import logging.handlers
import sys
import traceback

import requests

try:
    from .loggly_futures_session import LogglyHandler
except Exception as exc:
    raise Exception(exc)
