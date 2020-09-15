"""Classes and functions for working with and validating the Reactor context
"""
import functools
import glob
import json
import os
import importlib
from .jsonmessages import validate_message, load_schema


def find_context_schema_files():
    """Searches defined filesystem locations for a context.jsonschema
    """
    schema_files = []
    DIRS = [os.path.join(os.getcwd(), 'schemas'), os.getcwd(), '/schemas', '/']
    for d in DIRS:
        result = glob.glob(os.path.join(d, 'context.jsonschema'))
        schema_files.extend(result)
    return schema_files

def union_context_schema(user_context_schema=None):
    """Generates a union schema between the user-provided and base context schemas.
    """
    if user_context_schema is None:
        user_context_schemas = find_context_schema_files()
        if len(user_context_schemas) > 0:
            user_context_schema = user_context_schemas[0]
    schema = get_union_context_schema()
    base_context_schema = get_base_context_schema()
    # Performs an outer merge on the provided schemas
    schema['allOf'].append(base_context_schema)
    if user_context_schema is not None:
        # TODO - force allow additional properties
        schema['allOf'].append(user_context_schema)
    return schema

def get_pkg_schema(namespace, filename):
    """Reads a JSON-formatted file with name `filename` that exists in a
    package `namespace`, and returns parsed file contents as a dict. Uses
    `importlib.resources` to discover package resources.
    """
    with importlib.resources.open_text(namespace, filename) as f:
        schema = json.load(f)
    return schema

def get_base_context_schema():
    return get_pkg_schema("reactors.schemas", "BaseContext.jsonschema")

def get_union_context_schema():
    return get_pkg_schema("reactors.schemas", "AbacoUnionContext.jsonschema")

