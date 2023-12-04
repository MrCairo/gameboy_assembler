"""Label Handling classes."""


import string
from singleton_decorator import singleton
from enum import IntEnum, auto

import constants


class LabelType(Enum):
    GLOBAL = auto()
    LOCAL = auto()
    RELATIVE = auto()


###############################################################################


class Label:
    """Represents a label which is used to represent an address or constant.

       Represents a label which is, in turn, used to represent an address
        or a constant in the program.
        - name:
            The text identifier of the Label
        - value:
            A numeric 16-bit value that can represent a value up to 16-bits.

        Optional:
        - constant:
            Constants can only be alpha character. This means that a constant
            CANNOT begine with a "." or end with a ":" or "::".

            Note: The value of a contant can be less than 0 or greater than
                  65535.
        - base:
            A numeric address (can be an expression like $FFD2). This defaults
            to the current identified SECTION as reported by the
            InstructionPointer object.
        """

    def __init__(self, name: str):
        if name is None or len(name) == 0:
            raise ValueError("Label name cannot be none or an empty string.")
        self._name = name

    def __init__(self, name: str, value: int, constant: bool = False):
        """Initialize a new Label object."""
