import os
import json
import pytest
from reactors import context


@pytest.mark.parametrize("namespace,filename,exception", (
    # A schema that ships with the package
    ("reactors.schemas", "BaseContext.jsonschema", None),
    # Another schema that ships with the package
    ("reactors.schemas", "AbacoUnionContext.jsonschema", None),
    # A file that DNE
    ("reactors.schemas", "bogus_schema.py", FileNotFoundError),
    # A file that is not a jsonschema
    ("reactors.schemas", "__init__.py", json.decoder.JSONDecodeError),
    # A non-existent module namespace
    ("reactors.bogus_namespace", "BaseContext.jsonschema", ModuleNotFoundError),
))
def test_get_pkg_schema(namespace, filename, exception):
    """
    """
    f = context.get_pkg_schema
    args = (namespace, filename)

    if exception is None:
        result = f(*args)
        assert isinstance(result, dict)
    else:
        with pytest.raises(exception):
            _ = f(*args)


def test_get_base_context_schema():
    result = context.get_base_context_schema()
    assert isinstance(result, dict)


def test_get_union_context_schema():
    result = context.get_union_context_schema()
    assert isinstance(result, dict)
