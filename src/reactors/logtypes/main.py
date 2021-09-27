'''
Set up a logger with optional support for a logfile and STDERR reporting

Usage: logger = get_logger(name, log_level, log_file)
'''
from __future__ import unicode_literals

import json
import os
import time
import logging
import logging.config
from types import MethodType

from os import path
from .slack import SlackHandler
from .logstash import LogstashPlaintextHandler
from .loggly import LogglyHandler


# don't redact strings less than this size
MIN_REDACT_LEN = 4
# possible log levels
LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG')
# default log file to be used when using the the combined strategy
LOG_FILE = None
# default log level
LOG_LEVEL = 'DEBUG'

# log strategies that can be used. with combined, all logs go to one file;
# with split, each pikaview has its own log file.
LOG_FILE_STRATEGIES = ('split', 'combined')

# default log strategy
LOG_FILE_STRATEGY_DEFAULT = 'combined'

# Working directory - home of logs
PWD = os.getcwd()

DEFAULT_LOGGLY_URL = 'https://logs-01.loggly.com/inputs/{customer_token}/tag/python'


def get_log_file_strategy():
    return LOG_FILE_STRATEGY_DEFAULT


def get_log_file(name):
    return LOG_FILE


def redact_decorator(func, patterns):
    def wrapper_func(*args, **kwargs):
        msg = func(*args, **kwargs)
        for pattern in patterns:
            if len(pattern) > MIN_REDACT_LEN:
                msg = msg.replace(pattern, "*****")
        # return msg
    return wrapper_func


class RedactingFormatter(logging.Formatter):
    """Specialized formatter used to sanitize log messages"""
    converter = time.gmtime

    def __init__(self, *args, patterns=None, **kwargs):
        super(RedactingFormatter, self).__init__(*args, **kwargs)
        if patterns is None:
            patterns = list()
        self._patterns = patterns
        # self.orig_format = super(RedactingFormatter, self).format

    def format(self, record):
        msg = logging.Formatter.format(self, record)
        for pattern in self._patterns:
            if len(pattern) > MIN_REDACT_LEN:
                msg = msg.replace(pattern, "*****")
        return msg


def _get_logger(name, subname, log_level):

    logger_name = '.'.join([name, subname])
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    return logger


def _get_formatter(name, subname, redactions, timestamp):

    if timestamp is False:
        LOG_FORMAT = "{} %(levelname)s %(message)s".format(name)
    else:
        LOG_FORMAT = "{} %(asctime)s %(levelname)s %(message)s".format(name)

    DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"
    f = RedactingFormatter(fmt=LOG_FORMAT, datefmt=DATEFORMAT, patterns=redactions)
    # f.converter = 
    # breakpoint()
    # f.format = MethodType(redact_decorator(f.format, patterns=redactions), f)
    # f.format = redact_decorator(f.format, patterns=redactions)
    # f = RedactingFormatter(f, patterns=redactions)
    return f


def _get_logstash_formatter(name, subname, redactions, fields, timestamp):

    logstruct = {'timestamp': '%(asctime)s',
                 'message': '%(message)s',
                 'level': '%(levelname)s'}
    for (k, v) in list(fields.items()):
        logstruct[k] = v

    JSON_FORMAT = json.dumps(logstruct, indent=None, separators=(',', ':'))
    DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"

    f = RedactingFormatter(fmt=JSON_FORMAT, datefmt=DATEFORMAT, patterns=redactions)
    return f



def _get_loggly_formatter(name, subname, redactions, fields, timestamp):

    logstruct = {'timestamp': '%(asctime)s',
                 'message': '%(message)s',
                 'level': '%(levelno)s',
                 'lineNo': "%(lineno)d",
                 "logRecordCreationTime": "%(created)f"}

    for (k, v) in list(fields.items()):
        logstruct[k] = v

    JSON_FORMAT = json.dumps(logstruct, indent=None, separators=(',', ':'))
    DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"

    f = RedactingFormatter(fmt=JSON_FORMAT, datefmt=DATEFORMAT, patterns=redactions)
    return f


def get_screen_logger(name,
                      subname=None,
                      settings={},
                      redactions=[],
                      fields={},
                      timestamp=False):

    log_level = settings.get('logs', {}).get('level', LOG_LEVEL)
    logger = _get_logger(name=name, subname=subname,
                         log_level=log_level)

    # Create the STDERR logger
    text_formatter = _get_formatter(name, subname, redactions, timestamp)
    stderrHandler = logging.StreamHandler()
    stderrHandler.setFormatter(text_formatter)
    logger.addHandler(stderrHandler)

    # Create FILE logger (mirror)
    log_file = settings.get('logs', {}).get('file', None)
    if log_file is not None:
        log_file_path = os.path.join(PWD, log_file)
        fileHandler = logging.FileHandler(log_file_path)
        fileHandler.setFormatter(text_formatter)
        logger.addHandler(fileHandler)

    # Create NETWORK logger if log_token present
    log_token = settings.get('logs', {}).get('token', None)
    config = settings.get('logger', None)
    if log_token is not None and config is not None:
        json_formatter = _get_logstash_formatter(name, subname,
                                                 redactions,
                                                 fields,
                                                 timestamp)

        networkHandler = LogstashPlaintextHandler(config, log_token)
        networkHandler.setFormatter(json_formatter)
        logger.addHandler(networkHandler)

    # TODO: Forward to log aggregator if token is set
    return logger


# def get_stream_logger(name, subname, config, token,
#                       log_level=LOG_LEVEL,
#                       redactions=[],
#                       timestamp=False,
#                       fields={}):
#     logger = _get_logger(name=name, subname=subname, log_level=LOG_LEVEL,
#                          redactions=redactions)
#     formatter = _get_logstash_formatter(name, subname,
#                                         redactions, fields, timestamp)

#     streamLogger = LogstashPlaintextHandler(config, token)
#     streamLogger.setFormatter(formatter)
#     logger.addHandler(streamLogger)
#     return logger


def get_slack_logger(name, subname,
                     settings={},
                     redactions=[],
                     timestamp=False):

    '''Returns a logger object that can post to Slack'''
    log_level = settings.get('logs', {}).get('level', LOG_LEVEL)
    logger = _get_logger(name=name, subname=subname, log_level=log_level)
    text_formatter = _get_formatter(name, subname, redactions, timestamp)
    slacksettings = settings.get('slack', {})
    slackHandler = SlackHandler(slacksettings)
    slackHandler.setFormatter(text_formatter)
    logger.addHandler(slackHandler)
    return logger


def get_loggly_logger(name,
                      subname=None,
                      settings={},
                      redactions=[],
                      fields={},
                      timestamp=False):
    '''Returns a logger object that can post to Loggly'''

    log_level = settings.get('logs', {}).get('level', LOG_LEVEL)
    logger = _get_logger(name=name, subname=subname, log_level=log_level)

    # Create the STDERR logger
    text_formatter = _get_formatter(name, subname, redactions, timestamp)
    stderrHandler = logging.StreamHandler()
    stderrHandler.setFormatter(text_formatter)
    logger.addHandler(stderrHandler)

    # Construct the Loggly URL
    config = settings.get('loggly', dict())
    url = config.get('url', '')
    customer_token = config.get('customer_token')
    if customer_token is None:
        customer_token = str()
    if not url:
        url = DEFAULT_LOGGLY_URL
    url = url.replace('{customer_token}', customer_token)

    # Create LogglyHandler if loggly config is present
    if config and customer_token:
        json_formatter = _get_loggly_formatter(name, subname, redactions, fields, 
                                               timestamp)
        loggly_handler = LogglyHandler(url=url)
        loggly_handler.setFormatter(json_formatter)
        logger.addHandler(loggly_handler)

    # TODO: Forward to loggly if token is set
    return logger


def get_logger(name, subname=None, log_level=LOG_LEVEL, log_file=None,
               redactions=[], timestamp=False):
    '''Legacy alias to get_stderr_logger'''
    return get_screen_logger(name, subname, log_level, redactions)

# Verified Py3 compatible
