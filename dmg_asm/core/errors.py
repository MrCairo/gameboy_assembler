"""Error recording classes."""

from enum import Enum, auto


class ErrorCode(Enum):
    """Instruction error codes."""
    INVALID_MNEMONIC = auto()
    INCOMPLETE_INSTRUCTION = auto()
    INVALID_OPERAND = auto()
    OPERAND_IS_NOT_NUMERIC = auto()
    MISSING_MACHINE_CODE = auto()
    INVALID_LABEL_NAME = auto()
    INVALID_LABEL_POSITION = auto()
    INVALID_SYMBOL_NAME = auto()
    INVALID_SYMBOL_POSITION = auto()
    INVALID_REGISTER = auto()
    INVALID_REGISTER_POSITION = auto()
    INVALID_SECTION_POSITION = auto()
    INVALID_DECLARATION = auto()
    INVALID_SYNTAX = auto()
    INVALID_EQUATE_SYMBOL = auto()
    INVALID_EQUATE_EXPRESSION = auto()
    # Eventually have Warnings here as well?


# ##############################################################################

class Error:
    """Represents an Error object used in Instruction related operations."""

    __messages = {
        ErrorCode.INVALID_MNEMONIC:
        "Error: Invalid mnemonic",

        ErrorCode.INCOMPLETE_INSTRUCTION:
        "Error: Incomplete instrution. One or more operands are missing",

        ErrorCode.INVALID_OPERAND:
        "Error: The operand provided is invalid",

        ErrorCode.MISSING_MACHINE_CODE:
        "Error: The resulting instruction did not produce any machine code",

        ErrorCode.INVALID_LABEL_NAME:
        "Error: The symbol name is not in a valid format.",

        ErrorCode.INVALID_LABEL_POSITION:
        "Error: The symbol name is not in a valid position.",

        ErrorCode.INVALID_SYMBOL_NAME:
        "Error: The symbol name is not in a valid format.",

        ErrorCode.INVALID_SYMBOL_POSITION:
        "Error: The symbol name is not in a valid position.",

        ErrorCode.INVALID_REGISTER:
        "Error: The register is not a valid register",

        ErrorCode.INVALID_REGISTER_POSITION:
        "Error: The use of the register in this position is invalid",

        ErrorCode.OPERAND_IS_NOT_NUMERIC:
        "Error: The operand was not a valid numeric value",

        ErrorCode.INVALID_SECTION_POSITION:
        """Error: The SECTION declaration must be the first declaration in
        "the file.""",

        ErrorCode.INVALID_DECLARATION:
        """The declaration was not a know keyword or instruction or appears
        with invalid characters or spacing.""",

        ErrorCode.INVALID_SYNTAX:
        "The syntax of line cannot be determined."
    }

    def __init__(self, error_code: int, supplimental: str = "",
                 source_file: str = None, source_line: int = None):
        self._code: ErrorCode = error_code
        self._supplimental = supplimental
        self._file = source_file
        self._line = source_line

    def __str__(self):
        if self._code in Error.__messages:
            message = Error.__messages[self._code]
            if self._supplimental:
                message += ": [" + self._supplimental + "]"
            if self._file:
                line = str(self._line) if not None else "?"
                message += f"\nLocation: {self._file}:{line}\n"
        else:
            message = f"ERROR: Invalid error code: [{self._code}]"
        return message

    @ property
    def code(self) -> ErrorCode:
        """ Returns the error code passed when creating this Error object."""
        return self._code

    @ property
    def supplimental(self) -> str:
        """ Returns the supplimental text passed when creating this Error
        object. """
        return self._supplimental

    @ property
    def source_file(self) -> str:
        """Return the reported source file that created the Error."""
        return self._file

    @ property
    def source_line(self) -> int:
        """Return the reported source line of the source file of the Error."""
        return self._line
