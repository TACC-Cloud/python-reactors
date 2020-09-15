import pytest
import os
import sys

from reactors.agaveutils.entity import is_appid

@pytest.mark.parametrize("appid,result", [
    ('the-taconator-0.1.0', True),
    ('the_taconator-0.1.0', True),
    ('the-taconator-0.1', True),
    ('the-taconator-0', False),
    ('the_taconator-0', False),
    ('the-taconator-0.1.0u1', True),
    ('the-taconator-0.1.0u12', True),
    ('the-taconator-0.1.0u12a', False),
    ('the-biggest-baddest-baconyest-beanyest-taconator-ever-made-0.1.0u12', False)
])
def test_is_appid(appid, result):
    assert is_appid(appid) is result
