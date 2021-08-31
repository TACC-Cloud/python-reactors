import os
import pytest
import json
import jsonschema
from reactors.validation import jsondoc as jsonmessages, message as message_module
import logging
from pprint import pformat as pf


@pytest.fixture
def r(r_tp_opt):
    return r_tp_opt


@pytest.fixture
def R(R_tp_opt):
    return R_tp_opt


@pytest.fixture
def tests_data_dir():
    return os.path.join(os.getcwd(), 'tests', 'data')


@pytest.fixture
def static_paths(tests_data_dir):
    return [
        os.path.join(tests_data_dir, 'schemas', "AbacoMessageEmail.jsonschema"), 
        os.path.join(tests_data_dir, 'schemas', "AbacoMessageSQS.jsonschema")
    ]


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


def test_find_schema_files(change_test_dir, tests_data_dir):
    '''Test that >1 schema files can be discovered in the test environment.
    Expects schema files located in tests/data/schemas.
    '''
    assert not jsonmessages.find_schema_files()
    change_test_dir(tests_data_dir)
    schema_files = jsonmessages.find_schema_files()
    assert len(schema_files) >= 2


def test_find_schema_files_static_paths(static_paths):
    '''Test that >1 schema files can be discovered in the test environment
    when using `static_paths` kwarg.'''
    schema_files = jsonmessages.find_schema_files(static_paths=static_paths)
    og_n_matches = len(schema_files)
    assert og_n_matches >= 2


def test_find_schema_files_no_dup(tests_data_dir, change_test_dir, static_paths):
    '''Test that >1 schema files added from `static_paths` kwarg are not 
    appended as duplicates if they were already found.
    '''
    change_test_dir(tests_data_dir)
    no_static = jsonmessages.find_schema_files()
    og_n_matches = len(no_static)
    assert og_n_matches >= 2

    # check that matches are not added twice if using static_paths
    w_matches = jsonmessages.find_schema_files(static_paths=static_paths)
    assert len(w_matches) == og_n_matches


def test_classify_simple_json_message(change_test_dir, tests_data_dir):
    '''Test that simple JSON can be classified with only the generic (Default) 
    schema
    '''
    # discover our test message schemas
    change_test_dir(tests_data_dir)

    message = json.loads('{"aljsydgflajsgd": "FKJHFKJLJHGL345678"}')
    matches = message_module.classify_message(message, permissive=True)
    logging.debug(f"matches: {pf(matches)}")
    assert len(matches) == 1
    assert 'Default' in [m['$id'] for m in matches]


def test_classify_email_json_message(change_test_dir, tests_data_dir):
    '''Test that an email message can be classified with the generic and email message schema'''
    # discover our test schemas
    change_test_dir(tests_data_dir)

    message = json.loads('{"to": "tacc@email.tacc.cloud"}')
    matches = message_module.classify_message(message)
    logging.debug(f"matches: {pf(matches)}")
    match_ids = list()
    for match in matches:
        assert isinstance(match, dict)
        match_ids.append(match['$id'])
    assert 'Default' in [m['$id'] for m in matches]
    assert 'abaco_json_email' in [m['$id'] for m in matches]

