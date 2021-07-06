import pytest
import os
import sys
import json

import jsonschema
from reactors.runtime import Reactor
from reactors.validation import jsondoc as jsonmessages, message as message_module


# @pytest.mark.skip
def test_validate_named_message_jsonschema():
    '''Ensure singular message.jsonschema will validate'''
    r = Reactor()
    message = json.loads('{"key": "value"}')
    valid = r.validate_message(message,
                               schema='/message.jsonschema',
                               permissive=False)
    assert valid is True

# @pytest.mark.skip
def test_validate_message_jsonschema():
    '''Ensure singular message.jsonschema can be picked up via filesystem search'''
    r = Reactor()
    message = json.loads('{"key": "value"}')
    valid = r.validate_message(message,
                               permissive=False)
    assert valid is True

@pytest.mark.skip
def test_validate_message_jsonschema_throws_exception():
    '''Ensure ValidationError can be raised'''
    r = Reactor()
    message = []
    with pytest.raises(jsonschema.ValidationError):
        valid = r.validate_message(message,
                                permissive=False)

def test_fetch_schema_from_url():
    '''Test that schema can be retrieved from URL reference'''
    sch = jsonmessages.load_schema('https://json.schemastore.org/appveyor')
    assert isinstance(sch, dict)

@pytest.mark.parametrize("reference, success", [
    ('https://json.schemastore.org/appveyor', True),
    ('https://json.schemastore.org/dummy-appveyor', False),
    # ('file:///message.jsonschema', True),
    # ('/message.jsonschema', True),
    ('/message.txt', False),
    ('meep-meep-meep', False)])
def test_load_schema(reference, success):
    '''Test that schemas can be loaded from URL and file references'''
    if success is True:
        sch = jsonmessages.load_schema(reference)
        assert isinstance(sch, dict)
    else:
        with pytest.raises(Exception):
            sch = jsonmessages.load_schema(reference)

@pytest.mark.skip(reason='env specific')
def test_find_schema_files():
    '''Test that >1 schema files can be discovered in the test environment'''
    schema_files = jsonmessages.find_schema_files()
    assert len(schema_files) > 1

# def test_get_schema_identifier():
#     schemas = []
#     for sch in schemas:
#         jsonmessages.get_schema_identifier(sch)

@pytest.mark.skip
def test_classify_simple_json_message():
    '''Test that simple JSON can be classified with the generic schema'''
    r = Reactor()
    message = json.loads('{"aljsydgflajsgd": "FKJHFKJLJHGL345678"}')
    matches = message_module.classify_message(message, 
                                            permissive=True)
    assert len(matches) == 1
    assert 'abaco_json_message' in matches


@pytest.mark.skip
def test_classify_email_json_message():
    '''Test that an email message can be classified with the generic and email message schema'''
    r = Reactor()
    message = json.loads('{"to": "tacc@email.tacc.cloud"}')
    matches = message_module.classify_message(message)
    assert len(matches) >= 1
    assert 'abaco_json_email' in matches

