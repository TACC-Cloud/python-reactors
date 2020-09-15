"""Classes and functions for working with and validating JSON messages
"""
import glob
import functools
import json
import jsonschema
import os
import re
import requests
import validators

class formatChecker(jsonschema.FormatChecker):
    """Enables python-jsonschema to validate ``format`` fields"""
    def __init__(self):
        jsonschema.FormatChecker.__init__(self)

@functools.lru_cache(maxsize=32)
def find_schema_files():
    """Searches defined filesystem locations for candidate JSON schema files
    """
    schema_files = []
    DIRS = [os.path.join(os.getcwd(), 'schemas'), os.getcwd(), '/schemas', '/']
    for d in DIRS:
        result = glob.glob(os.path.join(d, '*.jsonschema'))
        schema_files.extend(result)
    return schema_files

@functools.lru_cache(maxsize=32)
def fetch_schema_from_url(url):
    """Fetches a schema document from a URL.
    """
    r = requests.get(url)
    r.raise_for_status
    return r.json()

def load_schema(schema):
    """Returns a materialized schema from dict, URL, or file.
    """
    if isinstance(schema, str):
        if validators.url(schema):
            return fetch_schema_from_url(schema)
        else:
            # remove file://
            schema = re.sub('^file://', '', schema)
            with open(schema) as schemaf:
                return json.loads(schemaf.read())
    # TODO - accept filehandle
    elif isinstance(schema, dict):
        # Enforce that the dict loads as JSON
        return json.loads(json.dumps(schema))
    else:
        raise ValueError('Value passed for schema must be dict, url, or filename')  

def get_schema_identifier(schema):
    """Returns an identifying string from a JSON schema.
    """
    try:
        # TODO - consider adding other methods to formulate an identifier
        return schema.get('$id')
    except KeyError:
        raise ValueError('Schema is missing an $id field')

def validate_message(message, schema, permissive=True):
    """Validates that a message conforms to the given schema.
    """
    try:

        jsonschema.validate(message, load_schema(schema), format_checker=formatChecker())
        return True
    except Exception:
        if permissive is True:
            return False
        else:
            raise

def classify_message(message, schemas=None, allow_multiple=True, permissive=True):
    """Classifies which (if any) provided schemas a message matches.
    """
    if schemas is None:
        schemas = find_schema_files()
        
    classifications = []
    for s in schemas:
        try:
            schema_dict = load_schema(s)
            validate_message(message, schema_dict, permissive=False)
            classifications.append(get_schema_identifier(schema_dict))
        except Exception:
            if permissive:
                pass
            else:
                raise
    if len(classifications) > 1 and allow_multiple is False:
        raise ValueError('Message matches >1 ({}) schemas'.format(len(classifications)))
    if len(classifications) == 0 and permissive is False:
        raise ValueError('Message matches no schemas')
    return classifications
