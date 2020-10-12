"""Derived Reactor class implementing validations
"""
from reactors import validation
from .base import BaseReactor

class Validation(BaseReactor):

    AUTO_VALIDATE_BINARY = False
    AUTO_VALIDATE_CONTEXT = True
    AUTO_VALIDATE_MESSAGE = True

    def validate_message(self,
                         message=None,
                         schema=None,
                         permissive=True):
        """
        Validate Actor message against a JSON schema

        Positional arguments:

        Keyword arguments:
            message - dict - representation of a JSON message
            schema - str - override path to a JSON schema file [/schemas/message.jsonschema]
            permissive - bool - swallow validation errors [True]
        """
        if message is None:
            message = self.message
        assert isinstance(message, dict), 'Message must be a <dict>'
        return validation.message.validate(message,
                                           permissive=permissive)

    def validate_context(self,
                         schema=None,
                         permissive=True):
        """
        Validate Actor context using a JSON schema

        Positional arguments:

        Keyword arguments:
            schema - str - override path to a JSON schema file [/schemas/context.jsonschema]
            permissive - bool - swallow validation errors [True]
        """
        return validation.context.validate(self.context, permissive=permissive)

    def validate_binary(self, validator=None, permissive=True):
        """(Stub) Verify Actor binary FIFO contents

        Positional arguments:

        Keyword arguments:
            validator - func - user function for validating a binary [binary.validator_function]
            permissive - bool - swallow validation errors [True]
        """
        return validation.binary.validate(self.binary, permissive=permissive)


    def validate(self, check_context=AUTO_VALIDATE_CONTEXT, check_message=AUTO_VALIDATE_MESSAGE, check_binary=AUTO_VALIDATE_BINARY, permissive=True):
        """Perform all validations using default settings
        """
        # Context
        if check_context:
            context_valid = self.validate_context(permissive=permissive)
        else:
            context_valid = True

        # Message
        if check_message:
            message_valid = self.validate_message(permissive=permissive)
        else:
            message_valid = True

        # Binary
        if check_binary:
            binary_valid = self.validate_binary(permissive=permissive)
        else:
            binary_valid = True

        return context_valid and message_valid and binary_valid
