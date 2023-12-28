"""Classes to handle symbols.

The SYMBOL is a simple way of keeping track of an address by providing a way to
associate an address with a humnan readable name - a Symbol.

Symbols are relative to the current SECTION of code. A Symbol cannot be
assigned a value, instead the symbol is either assigned the computed address
or to a non-addressable block of data. By default, a Symbol is assigned the
memory address pointed to by the InstructionPointer's current address.

Symbols that are non-addressible are a way to label a block of data, such as a
string, that are not directly stored in memory.

A quick set of terms:
**Symbol** means the entire Symbol including the ':' and '.' characters.
**Symbol Name** means the Symbol WITHOUT the ':' or '.' characters.

Symbols have the following format:
* Can be upper or lower-case alpha characters.
* Can contain numeric values as long as the symbol starts with an alpha.
* Can be one to 10 characters in length (excluding key characters)
* Must end with a single or double colon ':' or '::'. These are used
  to identify different type ofs symbol (see below).
* Can start with a '.' which is used to define the symbols scope.
* Can not contain a space.
* Must start at the beginning of a line
* Are NOT case-sensitive so "sym" and "Sym" refer to the same Symbol.

Symbols can be one of three types:

1. A **LOCAL** symbol: this is a symbol whos scope is that of the current
   source file only. A LOCAL symbol ends with a single ':'.

2. A **PRIVATE** symbol: this is a symbol who's scope is only within the
   current LOCAL or GLOBAL symbol. This also means that a minor symbol cannot
   be specified without first specifying a major symbol. A PRIVATE symbol must
   start with a '.' and also end with a single ':'. This symbol can only be
   referenced within it's current LOCAL or GLOBAL symbol. This also means that
   LOCAL symbol names need only be unique under the current LOCAL/GLOBAL
   symbol.

3. An **EXPORTED** (or GLOBAL) symbol: this is basically just a LOCAL system
   that is exported and can be used beyond just the current file.  A GLOBAL
   symbol is identified by trailing double colons '::'.

   Ex:
     localSymbol:     - Identified by a single colon
     .privateSymbol:  - Starts with a '.' and ends with a colon
     exported::       - LOCAL symbol that is exported and, by definition,
                        global.

  Discussion:
    A symbol must start with an upper or lower-cased alpha charater
    (a-z|A-Z|.)  or the '.' chatacter used to represent a minor symbol. A
    symbol must also end with a ':' or '::'.

    A Symbol can contain numeric characters (0-9) as long as the
    numeric value appears after an alpha character.

             Symbol::     - Valid GLOBAL symbol
             .symbol:     - Valid PRIVATE symbol (has to be defined after a
                            major symbol).
             symbol22     - Invalid symbol. Needs at least one trailing ':'
             .mySymbol    - Invalid - Missing trailing ':'
             42Fun:       - Invalid - Symbol can't start with a number.
             gr8          - Invalid - missing trailing ':' (or '::')
"""

import string
from enum import StrEnum

from singleton_decorator import singleton
from .constants import SYM, MAX_SYMBOL_LENGTH
from .exception import UpdateSymbolAddressError, ExpressionBoundsError, \
    ExpressionSyntaxError, InvalidSymbolName, InvalidSymbolScope
from .expression import Expression
from .descriptor import LBL_DSC
from ..cpu.instruction_pointer import InstructionPointer


class SymbolScope(StrEnum):
    """Symbol Scope Constants."""

    PRIVATE = "private-local"
    LOCAL = "global-local"
    GLOBAL = "global-exported"


class SymbolAffix(StrEnum):
    """Prefix and suffix values."""

    LOCAL = ":"
    PRIVATE = "."
    EXPORTED = "::"  # Same sa GLOBAL
    GLOBAL = "::"    # Same as EXPORTED

# ============================================================================


class SymbolUtils:
    """Symbol utility functions."""

    @classmethod
    def is_valid_symbol(cls, name: str) -> bool:
        """Return True if 'name' represents a valid symbol.

        This function checks the vailidity of the Symbol. Note that this
        function does not check to see if a symbol already exists or not.
        """
        try:
            # Can we create a symbol from the name?
            Symbol(name.strip(), 0x00)
        except (InvalidSymbolName, InvalidSymbolScope):
            return False
        return True

    @classmethod
    def clean_name(cls, name: str) -> str:
        """Return a name less the ending punctuation."""
        return name.strip(".:")

    @classmethod
    def valid_symbol_chars(cls):
        """Return a string of all valid characters of a symbol."""
        return string.ascii_letters + string.digits + ".:_"

    @classmethod
    def valid_name_chars(cls):
        """Return a string of only valid characters of a name."""
        return LBL_DSC.charset()

    @classmethod
    def valid_symbol_first_char(cls):
        """Return a string of all valid 1st characters of a symbol."""
        return string.ascii_letters + "."

    @classmethod
    def symbol_has_valid_chars(cls, name: str) -> bool:
        """Return True if the symbol only has supported chars."""
        valid = True
        chars = SymbolUtils.valid_symbol_chars()
        for c in name:
            if c in chars:
                continue
            valid = False
            break
        return valid

    @classmethod
    def name_has_valid_chars(cls, line: str) -> bool:
        """Return True if symbol's name contains valid chars."""
        valid = True
        clean = SymbolUtils.clean_name(line)
        try:
            Expression(f"'{clean}'")
        except (TypeError, ExpressionBoundsError, ExpressionSyntaxError):
            valid = False

        return valid

    # --------========[ End of class ]========-------- #


SU = SymbolUtils


class Symbol():
    """A String name used to represent an address in memory.

    The name of the Symbol must follow the convention described in this
    module. The `addressing` optional boolean specifies if this symbol
    represents a location in memory (address) or just an alias for something
    like a string or block of data. By default, the Symbol is defined as an
    Symbol that records an address.
    """

    def __init__(self, name: str, addressing: bool = bool(True)):
        """Initialize a new Symbol with addressing flag."""
        self._addressing = addressing
        if not name:
            raise InvalidSymbolName(name)

        self._original_symbol = name
        self._clean_name = SU.clean_name(name)

        self._scope = self._scope_and_validate(self.name)
        if self._scope is None:
            raise InvalidSymbolScope(self.name)

        if addressing is True:
            self._base_address = InstructionPointer().base_address
        else:
            self._base_address = None
        self._local_hash: str

    def __str__(self):
        """Describe the symbol."""
        scope = "unknown"
        if self._scope is not None:
            scope = self._scope

        desc = f"\nSymbol: {self.clean_name}"
        desc += f", scope: {scope}"

        if self._addressing:
            desc += f", address: 0x{self._base_address:04x}"
        else:
            desc += ", non-addressing"

        return desc

    def __repr__(self):
        """Return a description of this symbol object."""
        desc = f"Symbol(\"{self.name}\", "
        desc += f"addressing =  bool({self._addressing}))"
        return desc

    @staticmethod
    def typename():
        """Return the string name of this class's type."""
        return SYM

    @property
    def clean_name(self) -> str:
        """Return the cleaned valid symbol name."""
        return self._clean_name

    @property
    def name(self) -> str:
        """Return the name of the symbol from initialization."""
        return self._original_symbol

    @property
    def scope(self) -> SymbolScope:
        """Return the scope of the Symbol."""
        return self._scope

    @property
    def base_address(self) -> int:
        """
        Return the symbol's base address.

        The address that is associated with the location of the symbol.
        In this way it's different from it's value. The base address
        can be used to compute, for example, a relative distance between
        the reference to a symbol and the symbol's base address.
        """
        return self._base_address

    @base_address.setter
    def base_address(self, new_value: int):
        """
        Set the base address of the symbol.

        Sets the base address of the symbol. See the base_address property
        for more information on the functionality of the base address.
        """
        if self._addressing is False:
            raise UpdateSymbolAddressError()
        self._base_address = new_value

    # ----------===========[ End of public funcs ]===========---------- #

    def _scope_and_validate(self, name: str) -> SymbolScope:
        #
        if len(name) > MAX_SYMBOL_LENGTH or \
           self._has_valid_decorators(name) is False:
            return None
        symbol_scope = None
        if name.startswith(SymbolAffix.PRIVATE):
            symbol_scope = SymbolScope.PRIVATE
        elif name.endswith(SymbolAffix.EXPORTED):
            symbol_scope = SymbolScope.GLOBAL
        elif name.endswith(SymbolAffix.LOCAL):
            symbol_scope = SymbolScope.LOCAL

        return symbol_scope

    def _has_valid_decorators(self, name: str) -> bool:
        # Does the symbol only contain valid chars?
        # Does the symbol name (less decorators of ':' or '.') only contain
        # valid chars?

        if SU.symbol_has_valid_chars(name) is False or \
           SU.name_has_valid_chars(name) is False:
            return False

        # Symbol name must start with an alpha and cannot have
        # embedded "." or ":" characters.
        clean = self.clean_name
        if clean[0].isalpha is False or \
           clean.count(".") or \
           clean.count(":"):
            return False

        # Valid symbols are:
        # local:
        # .private (means private relative to the current local symbol)
        # global::

        stop_count = name.count(".")
        colon_count = name.count(":")

        extern = name.endswith("::") and \
            colon_count == 2 and \
            stop_count == 0

        local = name.endswith(":") and \
            colon_count == 1 and \
            stop_count == 0

        priv = name.startswith(".") and \
            not extern and \
            not local and stop_count == 1

        invalid = False
        # Symbol must be at least one of etxernal/local/private categories.
        invalid = not priv and not local and not extern
        # Symbol cannot have more than one '.' or more than two ':'
        invalid |= stop_count > 1 or colon_count > 2
        # Extern symbol cannot have any stop characters (.)
        invalid |= extern and stop_count
        # A  symbol cannot start with a colon or end with a stop
        invalid |= name.startswith(":") or name.endswith(".")

        return not invalid

    # --------========[ End of class ]========-------- #


@singleton
class Symbols(dict):
    """A specialized dictionary that maintains all symbols.

    Symbols()[a_key] = a_symbol
    a_symbol = Symbols()[a_key]

    """

    first_chars = string.ascii_letters + "."
    valid_chars = string.ascii_letters + string.digits + ".:_"

    _symbols = {}

    def __init__(self):
        """Initialize a Symbol object."""
        super().__init__()
        self._symbols = {}

    def __repr__(self):
        """Print the object."""
        desc = ""
        if self._symbols:
            for symbol in self._symbols:
                desc = symbol.__repr__()
        return desc

    def __getitem__(self, key: str) -> Symbol:
        """Return value for key."""
        sym = None
        if key:
            key = (key.lstrip(".")).rstrip(":.")
            key = key.upper()
        try:
            sym = self._symbols[key]
        except KeyError:
            return None
        return sym

    def __setitem__(self, key: str, value: Symbol):
        """Set item by key."""
        if not isinstance(value, Symbol):
            raise TypeError(value)
        self._symbols[value.clean_name().upper()] = value

    def find(self, key: str) -> Symbol:
        """Equal to the __get__() index function."""
        return self[key]

    def add(self, symbol: Symbol):
        """Add a new Symbol object to the dictionary."""
        if symbol is not None:
            self._symbols[symbol.clean_name().upper()] = symbol

    def remove(self, symbol: Symbol):
        """Remove a symbol from the dictionary.

        The clean_name of the symbol is used as the key of the element to
        remove.
        """
        if symbol is not None:
            found = self[symbol.clean_name().upper()]
            if found:
                new_d = dict(self._symbols)
                del new_d[symbol.clean_name().upper()]
                self._symbols = new_d

    def local_symbols(self) -> dict:
        """Return symbols that are local in scope."""
        d = {k: v for k, v in self.items() if v.is_scope_global is False}
        return d

    def global_symbols(self) -> dict:
        """Return symbols that are global in scope."""
        d = {k: v for k, v in self.items() if v.is_scope_global}
        return d

    def items(self) -> dict:
        """Return the dictionary of Symbol objects."""
        return self._symbols

    def remove_all(self):
        """Remove all objects from the dictionary."""
        self._symbols.clear()

    # --------========[ End of class ]========-------- #


# #############################################################################

# Quick unit tests of these classes.

# if __name__ == "__main__":
#     try:
#         print(Symbol("Hello", 100))
#         print(Symbol(".begin:", 0))
#     except TypeError as te:
#         print(f"{te}: The symbol was not a valid type/symbol.")
#     except ValueError as ve:
#         print(f"{ve} was invalid as a symbol")

#     def test_symbol():
#         symbol = Symbol('.GOTO_SYMBOL:', 0x1000)
#         if symbol is None:
#             print("Unable to create a symbol")
#         else:
#             Symbols().add(symbol)

#         if Symbols()['GOTO_SYMBOL']:
#             print("Symbol was found.")
#         else:
#             print("Unable to find the symbol.")
#             print(Symbols())

#    test_symbol()
