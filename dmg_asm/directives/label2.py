"""Label Handling classes."""


import string
from singleton_decorator import singleton
from enum import IntEnum

import constants


class LabelScope(IntEnum):
    LOCAL = 1
    GLOBAL = 2

###############################################################################


class Label(object):
    """Represents a label which is used to represent an address or constant."""

    def __init__(self, name: str, value: int, constant: bool = False):
        """Initialize a new Label object."""
        """
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
        from instruction_pointer import InstructionPointer
        if not name:
            raise ValueError(name)

        self._constant = False

        # Valid:
        #   .label:      (local non-constant label)
        #   .label::     (global non-constant label)
        #   Label        (local)
        self._scope = self._scope_and_validate(name)
        if self._scope is None:
            raise ValueError(name)

        self._original_label = name
        self._clean_label = (name.lstrip(".")).rstrip(":. ")
        self._value = value
        self._base_address = InstructionPointer().base_address
        self._local_hash: str
        self._constant = constant
        if constant:  # Override const
            self._constant = True

    def __str__(self):
        """Return a descriptive representation of this object."""
        is_const = "---"
        is_const = "Yes" if self._constant else "No"
        scope = "local" if self._scope == LabelScope.LOCAL else "global"
        desc = f"\nLabel: {self._original_label}\nvalue: 0x{self._value:04x} "
        desc += f"is constant: {is_const}"
        desc += f"\nScope: {scope}"
        return desc

    def __repr__(self):
        """Return a str representation of how to re-construct this object."""
        desc = f"Label(\"{self._original_label}\", {self._value}, " \
            f"constant={self._constant})"
        return desc

    @staticmethod
    def typename():
        """Return the string name of this class's type."""
        return constants.LBL

    def clean_name(self) -> str:
        """Return a cleaned valid label."""
        """The value is stripped of the first and last label characters"""
        return self._clean_label

    def name(self) -> str:
        """Return the original value of the valid label."""
        """It will start with a '.'"""
        return self._original_label

    def value(self) -> int:
        """Return the value passed when the object was created."""
        return self._value

    @property
    def is_constant(self) -> bool:
        """Return True if the label is a constant."""
        """
        Returns True if the label's value is considered a
        constant. Constant values do not change. For example Pi is a
        constant value whereas something like the address of where code is
        located in memory can change.
        """
        return self._constant

    @is_constant.setter
    def is_constant(self, new_value):
        """Set the constness of the value of the Label."""
        """Note, that this value in now way effects how the Label object
        operates. It's simply a way for the consumer of the Label to react to
        how this the value of the label should be interpreted."""
        self._constant = True if new_value is True else False

    def is_scope_global(self) -> bool:
        """Return True if the scope of the label is global."""
        return self._scope == LabelScope.GLOBAL

    @property
    def base_address(self) -> int:
        """Return the associated address of the label."""
        """
        Returns the assocated address associated with the location of the
        label. In this way it's different from it's value. The base address
        can be used to compute, for example, a relative distance between
        the reference to a label and the label's base address.
        """
        return self._base_address

    @base_address.setter
    def base_address(self, new_value: int):
        """Set the base address of the label."""
        """
        Sets the base address of the label. See the base_address property
        for more information on the functionality of the base address.
        """
        self._base_address = new_value

    def _scope_and_validate(self, name: str) -> LabelScope:
        valid = (name[0].isalpha or name[0] == ".") \
            and LabelUtils.name_valid_label_chars(name)
        self._scope = None

        # The . can only appear at the beginning of the string. It's
        # invalid if it appears anywhere else.
        valid = name.count(".") <= 1 if valid == True else False

        if not valid:
            return None

        colons = name.count(":")  # Do we have scope characters?
        if colons and colons <= 2:
            if valid and name.endswith(":") and colons == 1:
                self._scope = LabelScope.LOCAL

            if valid and name.endswith("::") and colons == 2:
                self._scope = LabelScope.GLOBAL

        if valid:
            from .instruction_set import InstructionSet
            clean = name.replace(":", "").replace(".", "").upper()
            valid = clean not in constants.DIRECTIVES
            valid = False if InstructionSet().is_mnemonic(clean) else True

        if self._scope is None:
            self._scope = LabelScope.LOCAL if valid else None
        return self._scope
    # --------========[ End of class ]========-------- #


class LabelUtils():
    @classmethod
    def is_valid_label(cls, name: str):
        """
        Returns True if 'name' would represent a valid label.  This function
        does not check the Labels() container for the given label name.
        """
        label = Label(name.strip(), 0x00)  # Can we create a label from it?
        return label is not None

    @classmethod
    def valid_label_chars(cls):
        """Returns an array (string)  of all valid characters of a label."""
        return string.ascii_letters + string.digits + ".:_"

    @classmethod
    def valid_label_first_char(cls):
        """Returns an array (string) of all valid 1st characters of a label"""
        return string.ascii_letters + "."

    @classmethod
    def name_valid_label_chars(cls, line: str):
        valid = True
        for c in line:
            if c in Labels().valid_chars:
                continue
            else:
                valid = False
                break
        return valid


# def is_valid_label(name: str):
#     """
#     Returns True if 'name' would represent a valid label.  This function
#     does not check the Labels() container for the given label name.
#     """
#     label = Label(name.strip(), 0x00)  # Can we create a label from it?
#     return label is not None

# def valid_label_chars():
#     """Returns an array (string)  of all valid characters of a label."""
#     return string.ascii_letters + string.digits + ".:_"

# def valid_label_first_char():
#     """Returns an array (string) of all valid 1st characters of a label"""
#     return string.ascii_letters + "."

# def name_valid_label_chars(line: str):
#     valid = True
#     for c in line:
#         if c in Labels().valid_chars:
#             continue
#         else:
#             valid = False
#             break
#     return valid


######################################################################


@singleton
class Labels(dict):
    """Dictionary to maintains all labels."""

    """
    Labels()[a_key] = a_label
    a_label = Labels()[a_key]
    """
    first_chars = string.ascii_letters + "."
    valid_chars = string.ascii_letters + string.digits + ".:_"

    _labels = {}

    def __init__(self):
        """Initialize a Labels dictionary once."""
        super().__init__()
        self._labels = dict()

    def __repr__(self):
        """Return a str representation of how to re-construct this object."""
        desc = ""
        if self._labels:
            for label in self._labels:
                desc = label.__repr__()
        return desc

    def __getitem__(self, key: str) -> Label:
        """Return the value identified by 'key'."""
        if key:
            key = (key.lstrip(".")).rstrip(":.")
            key = key.upper()
        if key in self._labels.keys():
            return None if key not in self._labels \
                else self._labels[key]
        return None

    def __setitem__(self, key: str, value: Label):
        """Set a value in the dictionary with a given key."""
        if not isinstance(value, Label):
            raise TypeError(value)
        self._labels[value.clean_name().upper()] = value

    def find(self, key: str) -> Label:
        """Equal to the __get__() index function."""
        return self[key]

    def add(self, label: Label):
        """Add a new Label object to the dictionary."""
        if label is not None:
            self._labels[label.clean_name().upper()] = label

    def remove(self, label: Label):
        """Remove a label from the dictionary.

        The clean_name of the label is
        used as the key of the element to remove.
        """
        if label is not None:
            found = self[label.clean_name().upper()]
            if found:
                new_d = dict(self._labels)
                del new_d[label.clean_name().upper()]
                self._labels = new_d
        return

    def local_labels(self) -> dict:
        """Return a dictionary of just local scoped labels."""
        d = {k: v for k, v in self.items() if v.is_scope_global is False}
        return d

    def global_labels(self) -> dict:
        """Return a dictionary of just globally scoped labels."""
        d = {k: v for k, v in self.items() if v.is_scope_global}
        return d

    def items(self) -> dict:
        """Return the dictionary of Label objects."""
        return self._labels

    def remove_all(self):
        """Remove all objects from the dictionary."""
        self._labels.clear()

    # --------========[ End of class ]========-------- #
