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

from __future__ import annotations
import string
from enum import StrEnum

from .exception import DescriptorException, InvalidSymbolName, \
    InvalidSymbolScope
from .expression import Expression
from .convert import Convert
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

    label: LBL_DSC = LBL_DSC

    @classmethod
    def is_valid_symbol(cls, name: str) -> bool:
        """Return True if 'name' represents a valid symbol.

        This function checks the vailidity of the Symbol. Note that this
        function does not check to see if a symbol already exists or not.
        """
        return cls.has_valid_name_characters(name) and \
            cls.has_valid_scope_designation(name)

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
        return LBL_DSC.charset

    @classmethod
    def valid_symbol_first_char(cls):
        """Return a string of all valid 1st characters of a symbol."""
        return string.ascii_letters + "."

    @classmethod
    def get_valid_scope(cls, name: str) -> SymbolScope:
        """Return the symbol's scope designation if valid."""
        scope = None
        if cls.has_valid_scope_designation(name):
            if name.startswith(SymbolAffix.PRIVATE):
                scope = SymbolScope.PRIVATE
            elif name.endswith(SymbolAffix.EXPORTED):
                scope = SymbolScope.GLOBAL
            elif name.endswith(SymbolAffix.LOCAL):
                scope = SymbolScope.LOCAL
        return scope

    @classmethod
    def has_valid_name_characters(cls, name: str) -> bool:
        """Return if the name has valid characters."""
        try:
            cls().label = cls.clean_name(name)
        except DescriptorException:
            return False
        return all(c in cls.valid_symbol_chars() for c in name)

    @classmethod
    def has_valid_scope_designation(cls, name: str) -> bool:
        """Return True if the name has valid decorator affixes for scope."""
        # A 'cleaned' symbol name needs to conform to the label descriptor.
        if cls.has_valid_name_characters(name) is False:
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
            not local and \
            stop_count == 1 and \
            colon_count <= 1

        invalid = False
        # Symbol must be local or global
        # invalid = not local and not extern
        # Symbol must be at least one of etxernal/local/private categories.
        invalid = invalid or (not priv and not local and not extern)
        # Symbol cannot have more than one '.' or more than two ':'
        invalid = invalid or (stop_count > 1 or colon_count > 2)
        # Extern symbol cannot have any stop characters (.)
        invalid = invalid or (extern and stop_count > 0)
        # A  symbol cannot start with a colon or end with a stop
        invalid = invalid or (name.startswith(":") or name.endswith("."))

        return not invalid

    # --------========[ End of class ]========-------- #


SU = SymbolUtils


class Symbol():
    """A String name used to represent an address in memory.

    The name of the Symbol must follow the convention described in this
    module. The 'base_address' represents the absolute address in memory
    for this symbol. Optionally, this object can be added to the 'Symbols'
    dictionary. Symbol names must be unique.
    """

    __slots__ = ('_original_symbol', '_scope', '_clean_name', 'base_address',
                 '_relative_symbol')
    _original_symbol: str
    _scope: SymbolScope
    _clean_name: str
    _relative_symbol: Symbol | None
    base_address: Expression

    def __init__(self, name: str, base_address: Expression,
                 relative_symbol: Symbol = None):
        """Initialize a new Symbol with a 16-bit address.

        'relative_symbol' can be used to represent a Symbol from which this
        new Symbol is relative to."""
        if not name or not SU.has_valid_name_characters(name):
            raise InvalidSymbolName(name)
        if not SU.has_valid_scope_designation(name):
            raise InvalidSymbolScope(name)
        self._original_symbol = name
        self._clean_name = SU.clean_name(name)
        self._scope = SU.get_valid_scope(name)
        self._relative_symbol = relative_symbol
        if base_address is None:
            base_address = InstructionPointer().curr_pos()
        self.base_address = base_address

    def __str__(self):
        """Describe the symbol."""
        scope = "unknown"
        if self._scope is not None:
            scope = self._scope
        hex_addr = Convert(self.base_address).to_hex16_string()
        desc = f"\nSymbol: {self.clean_name}"
        desc += f", scope: {scope}"
        desc += f", address: {hex_addr}"
        return desc

    def __repr__(self):
        """Return a description of this symbol object."""
        desc = f"Symbol(\"{self.name}\", {self.base_address})"
        return desc

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

    # --------========[ End of class ]========-------- #


class Symbols:
    """A specialized dictionary that maintains all symbols.

    Symbols()[a_key] = a_symbol
    a_symbol = Symbols()[a_key]

    """

    __slots__ = ('symbols', 'first_chars', 'valid_chars')
    first_chars: str
    valid_chars: str
    symbols: dict

    def __new__(cls):
        """Implement a singleton by returning the existing or new instance."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Symbols, cls).__new__(cls)
            cls.instance.symbols = {}
            cls.instance.first_chars = string.ascii_letters + "."
            cls.instance.valid_chars = string.ascii_letters + \
                string.digits + ".:_"
        return cls.instance

    def __repr__(self):
        """Print the object."""
        desc = ""
        if self.symbols:
            for symbol in self.symbols:
                desc = symbol.__repr__()
        return desc

    def __getitem__(self, key: str) -> Symbol:
        """Return value for key."""
        sym = None
        if key:
            key = (key.lstrip(".")).rstrip(":.")
            key = key.upper()
        try:
            sym = self.symbols[key]
        except KeyError:
            return None
        return sym

    def __setitem__(self, key: str, value: Symbol):
        """Set item by key."""
        if not isinstance(value, Symbol):
            raise TypeError(value)
        if key:
            key = (key.lstrip(".")).rstrip(":.")
            key = key.upper()
            self.symbols[key] = value
        else:
            raise KeyError("A key was not provided")

    def __delitem__(self, key: str):
        if key:
            key = (key.lstrip(".")).rstrip(":.")
            key = key.upper()
            self.symbols.pop(key)

    def find(self, key: str) -> Symbol:
        """Equal to the __get__() index function."""
        return self[key]

    def add(self, symbol: Symbol):
        """Add a new Symbol object to the dictionary."""
        if symbol is not None:
            self[symbol.name] = symbol

    def push(self, symbol: Symbol):
        """Add a new Symbol object to the dictionary."""
        self.add(symbol)

    def remove(self, symbol: Symbol):
        """Remove a symbol from the dictionary.

        The clean_name of the symbol is used as the key of the element to
        remove.
        """
        if symbol is not None:
            found: Symbol = self[symbol.clean_name.upper()]
            if found:
                del self[found.name.upper]

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
        return self.symbols

    def remove_all(self):
        """Remove all objects from the dictionary."""
        self.symbols.clear()

    # --------========[ End of class ]========-------- #
