"""Classes and functions for working with and validating JSON messages
"""
import functools
import glob
import hashlib
import json
import os
import re

import jsonschema
import requests
import validators
from hypothesis_jsonschema import from_schema

__all__ = ['find_schema_files', 'schema_from_url', 'load_schema', 
           'validate_document', 'classify_document', 'schema_ids', 
           'schema_id', 'id_for_schema', 'formatChecker', 
           'vars_from_schema', 'load_schemas', 'is_default']

FILENAME_GLOB = '*.jsonschema'
DIRNAME = 'schemas'
ID_PROPERTY = '$id'
DEFAULT_ID = 'Default'

class formatChecker(jsonschema.FormatChecker):
    """Enables python-jsonschema to validate ``format`` fields"""
    def __init__(self):
        jsonschema.FormatChecker.__init__(self)

# @functools.lru_cache(maxsize=32)
def find_schema_files(dirname=DIRNAME, filename_glob=FILENAME_GLOB, static_paths=None):
    """Searches defined filesystem locations for JSON schema files
    """

    schema_files = []

    # The preferred behavior is to search for .jsonschema files one of two defined locations
    # PWD, ROOT
    DIRS = [os.path.join(os.getcwd(), dirname), os.path.join(os.path.abspath(os.sep), dirname)]
    for d in DIRS:
        result = glob.glob(os.path.join(d, filename_glob))
        for r in result:
            if r not in schema_files:
                schema_files.append(r)

    # We permit loading from static locations if provided. This is how the submodules 
    # inject their bundlded default files and implement legacy behavior
    if static_paths is None:
        static_paths = []
    for pth in static_paths:
        if os.path.exists(pth) and pth not in schema_files:
            schema_files.append(pth)

    return schema_files

@functools.lru_cache(maxsize=32)
def schema_from_url(url, inject_id=True):
    """Fetches a schema document from a URL.
    """
    r = requests.get(url)
    r.raise_for_status
    schema = r.json()
    if ID_PROPERTY not in schema and inject_id:
        schema[ID_PROPERTY] = url
    return schema

def schema_from_file(file_name_or_handle, inject_id=True):
    if isinstance(file_name_or_handle, str):
        file_name_or_handle = re.sub('^file://', '', file_name_or_handle)
        with open(file_name_or_handle) as schemaf:
            schema = json.loads(schemaf.read())
            if ID_PROPERTY not in schema and inject_id:
                schema[ID_PROPERTY] = 'file://' + file_name_or_handle
            return schema
    else:
        raise TypeError('file_name_or_handle can only be a <str>')

def id_for_schema(schema_as_dict):
    """Generates a hash-based identifier for a schema document
    """
    serialized = json.dumps(schema_as_dict, indent=0, sort_keys=True, separators=(',', ':'))
    hl = hashlib.sha256()
    hl.update(serialized.encode('utf-8'))
    return 'autogen://' + hl.digest().hex()

def is_default(schema_as_dict):
    """Return true if a JSONschema is the built-in default
    """
    return id_for_schema(schema_as_dict) == DEFAULT_ID


def schema_from_dict(sdict, inject_id=True):
    schema = json.loads(json.dumps(sdict))        
    if ID_PROPERTY not in schema and inject_id:
        # Injects a unqiuely identifying but not informative id for the schema
        schema[ID_PROPERTY] = id_for_schema(schema)
    return schema

def load_schema(schema, inject_id=True, force_additional_properties=False):
    """
    Loads a schema from a URL, file path, or dictionary

    Arguments
        schema (str|dict): Schema reference
        inject_id (bool): Whether to force the schema to contain an $id property
        force_additional_properties (bool): Whether to force the schema to accept additional properties

    Returns:
        dict: A dictionary containing the JSON schema

    On error:
        Returns value of text

    """

    schema_obj = None

    try:
        if isinstance(schema, str):
            if validators.url(schema):
                schema_obj = schema_from_url(schema, inject_id=inject_id)
            else:
                schema_obj = schema_from_file(schema, inject_id=inject_id)
        # TODO - accept filehandle
        elif isinstance(schema, dict):
            # Enforce that the dict loads as JSON
            schema_obj = schema_from_dict(schema, inject_id=inject_id)
        else:
            raise ValueError('Value passed for schema must be dict, url, or filename')
    except Exception:
        raise

    if force_additional_properties:
        schema_obj['additionalProperties'] = True    

    return schema_obj

def load_schemas(schemas, inject_id=True, force_additional_properties=False):
    """
    Loads list of schema URLs, file paths, and dictionaries

    Arguments
        schemas (list): List of schema references
        inject_id (bool): Whether to force the schema to contain an $id property
        force_additional_properties (bool): Whether to force the schema to accept additional properties

    Returns:
        list: A list of JSON schemas

    On error:
        N/A
    """

    loaded = []
    if not isinstance(schemas):
        schemas = [schemas]
    for s in schemas:
        loaded.append(load_schema(s, inject_id=inject_id, force_additional_properties=force_additional_properties))
    return loaded

def schema_id(schema):
    """Returns the identifier from a JSON schema.
    """
    try:
        # TODO - consider adding other methods to formulate an identifier
        return schema.get(ID_PROPERTY)
    except KeyError:
        raise KeyError('Schema is missing an its identifier: {0}'.format(ID_PROPERTY))

def schema_ids(schemas):
    """Returns the identifiers from a list of JSON schemas
    """
    if isinstance(schemas, dict):
        schemas = [schemas]
    ids = []
    for s in schemas:
        id.append(schema_id(s))
    return ids

def validate_document(message, schema, check_formats=True, permissive=True):
    """Validates that a document conforms to the given JSON schema.

    Arguments
        message (dict): JSON document loaded as a dictionary
        schema (str|dict): JSON schema as a dictionary
        check_formats (bool): Whether to enforce format validation
        permissive (bool): Whether to return False rather than raise an Exception on error

    Returns:
        bool: Whether the validation succeeded

    On error:
        Returns jsonschema.ValidationError
    """

    try:
        if check_formats:
            jsonschema.validate(message, load_schema(schema), format_checker=formatChecker())
        else:
            jsonschema.validate(message, load_schema(schema))
        return True
    except Exception:
        if permissive is True:
            return False
        else:
            raise

def classify_document(message, schemas=None, min_allowed=1, max_allowed=-1, permissive=True):
    """Classifies which (if any) provided JSON schemas a document matches.
    """
    # Autodiscover schemas if not presented
    if schemas is None:
        schemas = find_schema_files()
    if not isinstance(schemas, list):
        raise TypeError('keyword argument "schemas" must be a list')
        
    matched_schemas = []

    for s in schemas:
        try:
            schema_dict = load_schema(s)
            if validate_document(message, schema_dict, permissive=True):
                matched_schemas.append(schema_dict)
        except Exception:
            raise
    
    try:
        # MinMax checks
        if len(matched_schemas) < min_allowed:
            raise ValueError('Message does no match at least {0} schema(s)'.format(min_allowed))    
        if max_allowed > 0 and len(matched_schemas) > max_allowed:
            raise ValueError('Message matches >{0} ({1}) schemas'.format(max_allowed, len(matched_schemas)))
    except Exception:
        if permissive:
            pass
        else:
            raise

    return matched_schemas

def vars_from_schema(schema, filter_private=False, private_prefix='_'):
    """Transforms a JSON schema into list of dict representations
    
    Note: This does not (and cannot) resolve JSON $ref subproperties
    """
    props = schema.get('properties', {})
    vars = []
    reqd = schema.get('required', [])
    for k, v in props.items():
        if filter_private is False or not k.startswith(private_prefix):
            rep = {}
            rep = {'id': k, 'type': v.get('type', None), 
                   'description': v.get('description', None),
                   'default': v.get('default', None)}
            if k in reqd:
                rep['required'] = True
            else:
                rep['required'] = False
            vars.append(rep)
    return vars

def example(schema, remote_refs=False):
    """Uses Hypothesis to generate an example document from a schema

    Does not currently support schemas with remote URI references
    """
    # It should be possible to implement a resolved schema using 
    # resolve_all_refs with a custom LocalResolver that implements resolve_remote 
    # https://github.com/Zac-HD/hypothesis-jsonschema/blob/master/src/hypothesis_jsonschema/_canonicalise.py
    #
    # I have tried this but jsonschema.RefResolver seems to have some flakiness, so 
    # tabling this for now
    sch = load_schema(schema)
    return from_schema(sch).example()
