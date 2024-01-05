"""Various descriptors for generating validated numeric values."""


from abc import ABC, abstractmethod
import string
from dataclasses import dataclass
from .constants import MinMax
from .exception import DescriptorMinMaxLengthError, \
    DescriptorMinMaxValueError, \
    DescriptorRadixDigitValueError, \
    DescriptorRadixError


@dataclass
class DescriptorArgs():
    """The format that describes a value."""
    __slots__ = ('chars', 'limits', 'base', 'charset')
    chars: MinMax
    limits: MinMax
    base: int
    charset: str

    def __str__(self) -> str:
        """Return a string representation of this object."""
        desc = f"Args(chars={self.chars}, limits={self.limits}, "
        desc += f"base={self.base})"
        return desc

# |-----------------============<***>=============-----------------|


class Validator(ABC):
    """Abstract class to validate something."""
    private_name = ""
    public_name = ""

    def __set_name__(self, owner, name):
        """Set a named attribute of a generic object."""
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        """Get the value of a named attribute."""
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        """Set the value of a named attribute."""
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value):
        """Override this in any subclass to validate the value."""


class OneOf(Validator):
    """Verifies that a value is one of a restricted set of options."""

    def __init__(self, *options):
        """Initialize the OneOf Object."""
        self.options = set(options)

    def __repr__(self) -> str:
        return f"OneOf({self.options})"

    def validate(self, value):
        """Validate the OneOf object with against specific value."""
        if value not in self.options:
            raise ValueError(
                f'Expected {value!r} to be one of {self.options!r}'
            )


# |-----------------============<***>=============-----------------|


class BaseDescriptor(Validator):
    """A class that represents a value with n chars of min/max values."""

    bases = {
        0: f"{string.ascii_letters}{string.digits}_",  # Label Type
        2: "01",
        8: string.octdigits,
        10: string.digits,
        16: string.hexdigits}

    def __init__(self, chars: MinMax, limits: MinMax, base=10):
        """Initialie the object with # of chars and min/max values.

        chars represent the min and max nummber of characters.
        limits represents the base-10 min/max values of this object.
        A base of 0 is reserved for strings which can consist of any
        uppercase letter or numbers 0-9. No spaces or punctuation.
        """
        if base not in self.bases:
            raise DescriptorRadixError(
                f'Base can only 2, 8, 10 or 16 but was {base}')
        self.args = DescriptorArgs(chars=chars,
                                   limits=limits,
                                   base=base,
                                   charset=self.bases[base])

    def __str__(self) -> str:
        """Return a string representation of this object."""
        return f"Descriptor: {self.args}"

    def charset(self) -> str:
        """Return the allowable characters for the object's base."""
        return self.args.charset

    def validate(self, value):
        """Validate this object against a specific value."""
        if not isinstance(value, str):
            raise TypeError(f'Expected {value!r} to be a str.')

        if all(c in self.args.charset for c in value) is False:
            msg = f"{value} bad base {self.args.base} chars."
            raise DescriptorRadixDigitValueError(msg)

        # -- chars validation --
        minmax = self.args.chars
        if len(value) not in range(minmax.min, minmax.max):
            if minmax.min < minmax.max-1:
                msg = f'{value} must be between {minmax.min} ' + \
                    f'and {minmax.max-1} characters'
            else:
                msg = f'{value} must be exactly {minmax.min} ' + \
                    'characters in length'
            raise DescriptorMinMaxLengthError(msg)

        # -- limits validation value transformed to base-10 --
        if self.args.base > 0:
            dec_val = int(value, self.args.base)
            minmax = self.args.limits
            if dec_val not in range(minmax.min, minmax.max):
                raise DescriptorMinMaxValueError(
                    f'{dec_val} outside range of {minmax.min}, {minmax.max}.')

    # ---- BaseDescriptor class ends here ----


# |-----------------============<***>=============-----------------|
#
# NOTE: For chars, MinMax is more of a range where the count of
#       characters must fall between, for example, 1 and 16 which
#       indicates a string that cannot exceed 15 (max-1).
#
DEC_DSC = BaseDescriptor(chars=MinMax(1, 6),
                         limits=MinMax(0, 65536),
                         base=10)
HEX_DSC = BaseDescriptor(chars=MinMax(2, 3),
                         limits=MinMax(0, 256),
                         base=16)
HEX16_DSC = BaseDescriptor(chars=MinMax(2, 5),
                           limits=MinMax(0, 65536),
                           base=16)
BIN_DSC = BaseDescriptor(chars=MinMax(2, 9),
                         limits=MinMax(0, 256),
                         base=2)
OCT_DSC = BaseDescriptor(chars=MinMax(1, 7),
                         limits=MinMax(0, 65536),
                         base=8)
LBL_DSC = BaseDescriptor(chars=MinMax(1, 16),
                         limits=MinMax(0, 0),
                         base=0)

# |-----------------============<***>=============-----------------|


class BaseValue:
    """Base class for a BaseDescriptor value."""

    _descr: BaseDescriptor
    _base: int
    _ftypes = {2: 'b', 8: 'o', 10: 'd', 16: 'X'}

    def __init__(self, desc: BaseDescriptor):
        """Initialize the base object."""
        # We need to save off the parms. The Validator's getter
        # will be called when accessing the _descr variable which will
        # return 'value' instead of the Validatior object.
        self._chars = desc.args.chars
        self._limits = desc.args.limits
        self._base = desc.args.base
        self._descr = BaseDescriptor(chars=desc.args.chars,
                                     limits=desc.args.limits,
                                     base=desc.args.base)

    def __repr__(self):
        """Return a string representation of how re-create this object."""
        bd_str = f"BaseDescriptor(chars={self._chars}, "
        bd_str += f"limits={self._limits}, "
        bd_str += f"base={self._base})"
        vision = f"BaseValue({bd_str})"
        return vision

    def __str__(self):
        """Return a string representation of this object."""
        _val = int(self._descr, self._base)
        _max = self._chars.max - 1
        _format = self._ftypes[self._base]
        _filled = f"{_val:0{_max}{_format}}"
        return _filled

    def charset(self):
        """Return the set of valid characters for this object."""
        return self._descr.charset()

# |-----------------============<***>=============-----------------|

# descriptor.py ends here.
