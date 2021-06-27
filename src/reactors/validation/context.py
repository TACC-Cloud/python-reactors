"""Implements context validation
"""
import json
import os

from .jsondoc import (FILENAME_GLOB, ID_PROPERTY, classify_document,
                      find_schema_files, validate_document, load_schema)

ROOT = '/'
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONTEXT_JSONSCHEMA = os.path.join(HERE, 'context.jsonschema')

# Directory to search for context schemas
DIRNAME = 'context_schemas'
# Ordered list of paths to search for context schemas before using filename globbing
STATIC_PATHS = ['/context_schemas/default.jsonschema', '/context_schemas/context.jsonschema', 
                '/schemas/context.jsonschema', '/context.jsonschema', DEFAULT_CONTEXT_JSONSCHEMA]

UNION_SCHEMA_TEMPLATE = '''
{
	"$schema": "http://json-schema.org/draft-07/schema#",
	"$id": "AbacoUnionContext",
	"title": "Union of Base and User-provided environment contexts",
	"allOf": []
}
'''

__all__ = ['classify_context', 'validate_context', 'validate']

def default_schema():
    return json.load(open(DEFAULT_CONTEXT_JSONSCHEMA, 'r'))

def allof_schema(context_jsonschema=None):
    """Generates a union schema between the user-provided and base context schemas.
    """
    schema = json.loads(UNION_SCHEMA_TEMPLATE)
    default_jsonschema = json.load(open(DEFAULT_CONTEXT_JSONSCHEMA, 'r'))
    # Performs an outer merge on the provided schemas
    schema['allOf'].append(default_jsonschema)
    schema[ID_PROPERTY] = default_jsonschema[ID_PROPERTY]
    if context_jsonschema is not None:
        # TODO - enforce that context_jsonschema is valid JSONschema
        schema['allOf'].append(context_jsonschema)
        schema[ID_PROPERTY] = context_jsonschema[ID_PROPERTY]
    return schema

def find_context_schema_files(dirname=DIRNAME, filename_glob=FILENAME_GLOB, static_paths=STATIC_PATHS):
    """Searches defined filesystem locations for JSON schema files defining Abaco contexts
    """
    return find_schema_files(dirname=dirname, filename_glob=filename_glob, static_paths=static_paths)

def validate_context(context, schema, check_formats=True, permissive=True):
    """Validates that a document conforms to the given context JSON schema.

    Arguments
        context (dict): Abaco context loaded as a dictionary
        schema (str|dict): JSON schema as a dictionary
        check_formats (bool): Whether to enforce format validation
        permissive (bool): Whether to return False rather than raise an Exception on error

    Returns:
        bool: Whether the validation succeeded

    On error:
        Returns jsonschema.ValidationError
    """
    # We have to build a union between the base context, which covers all the 
    # housekeeping and admin variables, and the provided schema which covers
    # URL parameters that are expected to be propagated by Abaco
    test_schema = allof_schema(schema)
    return validate_document(context, test_schema, check_formats=check_formats, permissive=permissive)

def classify_context(context, schemas=None, min_allowed=0, max_allowed=-1, permissive=True):
    """Classifies which (if any) provided JSON schemas a context matches.
    """
    # Over-ride the discovery process for schemas, then pass along to classify_document
    if schemas is None:
        schemas = find_context_schema_files()
    # Load from files since we have to contruct the unions
    schema_docs = [allof_schema(json.load(open(s))) for s in schemas]
    return classify_document(context, schemas=schema_docs, min_allowed=min_allowed, 
                             max_allowed=max_allowed, permissive=permissive)


def validate(context, permissive=True):
    """Verifies that a context is valid
    """
    # Must match at least 1 schema
    matches = classify_context(context, permissive=permissive)
    if len(matches) > 0:
        return True
    else:
        if permissive:
            return False
        else:
            raise ValueError("Unable to validate context")