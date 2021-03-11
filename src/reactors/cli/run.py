import importlib
import json
import os
import sys
from inspect import getdoc, signature

HERE = os.path.dirname(os.path.abspath(__file__))
PWD = os.getcwd()

MODULE = '/reactor.py'
FUNCTION = 'main'

def docstring(fn):
    return getdoc(fn)

def load_function(module=MODULE, function=FUNCTION):
    # Module is a script name
    if module.endswith('.py'):
        # Transform the filename and extract its path
        # so it can be loaded as a module by importlib
        #
        # Extend PYTHONPATH to parent of script
        sys.path.insert(0, os.path.dirname(module))
        # Trim .py
        module = os.path.basename(module)[:-3]
    mod = importlib.import_module(module)
    # Dies w AttributeError if function does not exist
    fn = getattr(mod, function)
    return fn

def run(module=MODULE, function=FUNCTION, args=None):
    """Load and run a function from a script or module
    """
    fn = load_function(module, function)
    # TODO - pass args if the loaded function is able tp accept them
    # https://docs.python.org/3/library/inspect.html#inspect.signature
    # sig = signature(fn)
    fn()
