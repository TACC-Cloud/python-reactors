import os
import pytest
import json
import jsonschema
from reactors.validation import jsondoc as jsonmessages, message as message_module


@pytest.fixture
def r(r_tp_opt):
    return r_tp_opt


def test_validate_named_message_jsonschema(r):
    '''Ensure singular message.jsonschema will validate'''
    message = json.loads('{"key": "value"}')
    assert r.validate_message(message, schema='/message.jsonschema', permissive=False)
    assert r.validate_message(message, permissive=False)

@pytest.mark.parametrize('message', (list(), str(), int()))
def test_invalid_message_type(r, message):
    """Raises AssertionError if message is not type dict"""
    with pytest.raises(AssertionError):
        valid = r.validate_message(message, permissive=False)
    # assert not r.validate_message(message, permissive=True)


def test_fetch_schema_from_url():
    '''Test that schema can be retrieved from URL reference'''
    sch = jsonmessages.load_schema('https://json.schemastore.org/appveyor')
    assert isinstance(sch, dict)


@pytest.mark.parametrize("reference, success", [
    ('https://json.schemastore.org/appveyor', True),
    ('https://json.schemastore.org/dummy-appveyor', False),
    ('file://tests/data/message.jsonschema', True),
    ('tests/data/message.jsonschema', True),
    ('tests/data/message.txt', False),
    ('meep-meep-meep', False)])
def test_load_schema(reference, success):
    '''Test that schemas can be loaded from URL and file references'''
    if success is True:
        sch = jsonmessages.load_schema(reference)
        assert isinstance(sch, dict)
    else:
        with pytest.raises(Exception):
            sch = jsonmessages.load_schema(reference)


def test_find_schema_files_static():
    '''Test that >1 schema files can be discovered in the test environment'''
    static_paths = [os.path.join('tests', 'data', 'abacoschemas')]
    for d in static_paths:
        assert os.path.isdir(d)
    schema_files = jsonmessages.find_schema_files(static_paths=static_paths)
    assert len(schema_files) >= 1


@pytest.mark.skip
def test_classify_simple_json_message():
    '''Test that simple JSON can be classified with the generic schema'''
    r = Reactor()
    message = json.loads('{"aljsydgflajsgd": "FKJHFKJLJHGL345678"}')
    matches = message_module.classify_message(message, permissive=True)
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

