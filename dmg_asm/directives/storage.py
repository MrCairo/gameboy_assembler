#
# DS, DB, DW, DL declarations
#
from dataclasses import dataclass

from ..core.constants import StorageType, STORAGE_DIRECTIVES
from ..core.descriptor import HEX16_DSC, HEX_DSC
from ..core.exception import StorageException, StorageValueError, \
    DescriptorException, DescriptorMinMaxLengthError, DescriptorMinMaxValueError
from ..core import Expression, Convert
from ..tokens import TokenGroup, TokenType, Token

# #############################################################################


@dataclass
class _ParserData:
    """Stores the parsing results. Only the data and address are accessible
    and then only as a read-only data (bytes) and an address property."""
    s_type: StorageType
    data: bytes
    address: Expression

    def __init__(self):
        self.s_type = None
        self.data: bytes = None
        self.address = None


class Storage:
    """Represent an amount of storage that is reserved or just defined."""
    _roamer = 0
    _tokens: TokenGroup
    _data: _ParserData

    def __init__(self, token_group: TokenGroup):
        if token_group is None or not isinstance(token_group, TokenGroup):
            raise TypeError("'token_group' must be a valid TokenGroup")
        self._tokens = token_group
        self._data = _StorageParser(token_group).parse()

    def __str__(self):
        return "Section Yea!"

    def __repr__(self):
        return f"Storage({self._tokens.__repr__()})"

    def bytes(self) -> bytes | None:
        """Get the data out."""
        return self._data.data

    @property
    def address(self) -> Expression:
        """Return the address of this Object or None if not yet assigned.

        The address is returned as a 16-bit Expression."""
        return self._data.address

    @address.setter
    def address(self, new_value: Expression) -> None:
        """Set the address of this Object to the given 16-bit Expression."""
        if new_value is None or not isinstance(new_value, Expression):
            msg = "The new address must be a valid 16-bit Expression."
            raise TypeError(msg)
        self._data.address = new_value


class _StorageParser:
    """
    Parses storage types in tokenized format.
    """
    types = {
        "DS": StorageType.BLOCK,
        "DB": StorageType.BYTE,
        "DW": StorageType.WORD,
        "DL": StorageType.LONG
    }

    _hex16: HEX16_DSC = HEX16_DSC
    _hex: HEX_DSC = HEX_DSC
    _results: _ParserData
    _tok_len: int = 0

    def __init__(self, token_group: TokenGroup):
        if token_group is None or not isinstance(token_group, TokenGroup):
            raise TypeError("'token_group' must be a valid TokenGroup object.")
        if len(token_group) == 0:
            raise ValueError("'token_group' must have at least one Token.")
        if token_group[0].value not in STORAGE_DIRECTIVES:
            raise StorageValueError("Storage type must be "
                                    "DS, DB, DW, or DL")
        self._tokens = token_group
        self._results = _ParserData()
        self._tok_len = len(token_group)

    def parse(self) -> _ParserData | None:
        """Parse the token group."""
        s_name = self._tokens[0].value
        if s_name not in self.types:
            return None
        s_type = self.types[s_name]
        match s_type:
            case StorageType.BLOCK:
                self._results = self._to_space()
            case StorageType.BYTE:
                self._results = self._to_space()
            case StorageType.WORD:
                self._results = self._to_space()
            case StorageType.LONG:
                self._results = self._to_space()
        return self._results

    def __str__(self):
        desc = "No Data"
        return desc

    def __repr__(self):
        desc = f"Storage({self._tokens.__repr__()})"
        return desc

    # -----=====< End of public methods >=====----- #

    def _to_space(self) -> _ParserData:
        """
        This method is to accept no more than 2 or more parameters. The first
        is the number of bytes to allocate with a maximum of 4096 (4 Kib). The
        remaining parameters (if any exist) are the single-byte values used to
        fill the storage. All expressions are AND'ed to be 8-bit only.
        space. The values are repeated until the space is filled.  If none are
        provided, the space is filled with $00."""
        size: Expression = Expression("$01")
        parsed = _ParserData()
        parsed.data = None
        parsed.s_type = StorageType.BLOCK

        # Get 1st Exression which is the Size. It should already exist in the
        # Token (created during token processing)
        if self._tok_len > 1:
            size = self._tokens[1].data
            if size is None or not isinstance(size, Expression):
                return None
        if self._tok_len <= 2:  # Just DS _size_ (or just DS) so quick exit
            parsed.data = bytes(size.integer_value)
            return parsed

        # The remaining values are 8-bit values that are to be stored in the
        # block, repeating until the block is filled. If not present, the block
        # value will be set to 0x00.
        values: int = []
        limit = min(size.integer_value,
                    max(size.integer_value, self._tok_len - 2))
        for idx, val in enumerate(self._tokens[2:]):
            if idx == limit:
                break
            values.append(Convert(val.data).to_hex().prefixless_value)
        hexstr = ""
        val_len = len(values)
        for idx in range(0, size.integer_value):
            val = values[idx % val_len]
            hexstr += val
        parsed.data: bytes = bytes.fromhex(hexstr)
        return parsed

    def _to_bytes(self) -> _ParserData:
        parsed = _ParserData()
        return parsed
