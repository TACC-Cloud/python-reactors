import pytest
import os
import sys
import json

from reactors.runtime import Reactor
import testdata

@pytest.fixture(scope='session')
def test_data():
    return testdata.AbacoJSONmessages().data()

@pytest.mark.skip
def test_validate_schema():
    '''Ensure at least one schema can validate'''
    r = Reactor()
    message = json.loads('{"key": "value"}')
    valid = r.validate_message(message,
                               schema='/message.jsonschema',
                               permissive=False)
    assert valid is True

@pytest.mark.skip
def test_abacoschemas(test_data):
    '''Test all known Abaco schemas'''
    r = Reactor()
    exceptions = []
    for comp in test_data:
        mdict = comp.get('object', {})
        schem = os.path.join('/abacoschemas', comp.get('schema'))
        # perm = True
        validates = comp.get('validates')
        try:
            r.validate_message(mdict,
                               schema=schem,
                               permissive=False)
        except Exception as e:
            # The message did not validate tho we expected it to
            if validates is True:
                exceptions.append(e)

    if len(exceptions) > 0:
        raise Exception("Exceptions: {}".format(exceptions))
