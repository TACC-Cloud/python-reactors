from time import sleep, time

import pytz
import requests

__all__ = ['get_host_ip', 'microseconds', 'utcnow']

def get_host_ip():
    """Returns current IP address of host
    """
    try:
        return requests.request('GET', 'http://myip.dnsomatic.com').text
    except Exception:
        return 'localhost'

def microseconds():
    """Returns current time in microseconds
    """
    return int(round(time() * 1000 * 1000))

def utcnow():
    """Returns a text-formatted UTC date

    Example: 2018-01-05T18:40:55.290790+00:00
    """
    t = datetime.datetime.now(tz=pytz.utc)
    return t.isoformat()
