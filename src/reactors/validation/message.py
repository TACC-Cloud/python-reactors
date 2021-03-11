"""Implements JSON message validation
"""
import json
import os
import warnings

from hypothesis.errors import NonInteractiveExampleWarning
from hypothesis_jsonschema import from_schema

from .jsondoc import (FILENAME_GLOB, classify_document, find_schema_files,
                      is_default, load_schema, validate_document)

ROOT = '/'
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MESSAGE_JSONSCHEMA = os.path.join(HERE, 'message.jsonschema')

DIRNAME = 'message_schemas'
# Ordered list of paths to search first for context schemas
STATIC_PATHS = ['/message_schemas/default.jsonschema', '/message_schemas/message.jsonschema', 
                '/schemas/message.jsonschema', '/message.jsonschema', DEFAULT_MESSAGE_JSONSCHEMA]

def find_message_schema_files(dirname=DIRNAME, filename_glob=FILENAME_GLOB, static_paths=STATIC_PATHS):
    """Searches defined filesystem locations for JSON schema files defining Abaco message formats
    """
    return find_schema_files(dirname=dirname, filename_glob=filename_glob, static_paths=static_paths)

def validate_message(message, schema, check_formats=True, permissive=True):
    """Validates that a message conforms to the given message JSON schema.

    Arguments
        message (dict): Abaco message loaded as a dictionary
        schema (str|dict): JSON schema as a dictionary
        check_formats (bool): Whether to enforce format validation
        permissive (bool): Whether to return False rather than raise an Exception on error

    Returns:
        bool: Whether the validation succeeded

    On error:
        Returns jsonschema.ValidationError
    """
    return validate_document(message, schema, check_formats=check_formats, permissive=permissive)

def classify_message(message, schemas=None, min_allowed=0, max_allowed=-1, permissive=True):
    """Classifies which (if any) provided JSON schemas a message matches.
    """
    # Over-ride the discovery process for schemas, then pass along to classify_document
    if schemas is None:
        schemas = find_message_schema_files()
    return classify_document(message, schemas=schemas, min_allowed=min_allowed, 
                             max_allowed=max_allowed, permissive=permissive)

def validate(message, permissive=True):
    """Verifies that a message is valid according to one of the schemas
    """
    # Must match at least 1 schema
    matches = classify_message(message, permissive=permissive)
    if len(matches) > 0:
        return True
    else:
        if permissive:
            return False
        else:
            raise ValueError("Unable to validate message")

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

    # NOTE: Hypothesis warns us against using `.example()` However, we
    # are not using hypothesis in a conventional manner, and therefore this
    # warning does not apply here
    warnings.filterwarnings('ignore', category=NonInteractiveExampleWarning)
    sch = load_schema(schema)
    if is_default(sch):
        return dict()
    else:
        return from_schema(sch).example()
