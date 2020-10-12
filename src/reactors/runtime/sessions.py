"""Code having to do with actor sessions
"""
URL_PARAM = 'x_session'
ENVIRONMENT_VAR = 'SESSION'

def get_session(context, default=None):
    return context.get(URL_PARAM, context.get(ENVIRONMENT_VAR, default))
