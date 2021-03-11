"""Implements binary validation
"""
from agavepy.actors import get_binary_message
# from .binaryvalidators import *

__all__ = ['validate_binary', 'classify_binary', 'validate']

def find_binary_validators():
    return []

def validate_binary(binary, validator, permissive=True):
    return True

def classify_binary(binary, validators=None, permissive=True):
    return None

def validate(binary, permissive=True):
    return True
