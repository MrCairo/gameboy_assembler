"""Specialized Exception classes."""


class ParserException(Exception):
    """Base class of exceptions for the parser."""

    def __init__(self, message, line_text=None, line_number=None):
        """Initialize the exception."""
        filename = line_text if line_text is not None else "unk_file"
        lineno = line_number if line_number is not None else "unk_line"

        new_message = f"{message} [{filename}:{lineno}]"
        super().__init__(new_message)
        self.line_text = line_text
        self.line_number = line_number


class DefineDataError(ParserException):
    """An exception that occurs when a data define is invalid.

    These are errors that are thrown when processing the DS, DB,
    DW, or DL sections.
    """

    def __init__(self, message, line_text="", line_number=-1):
        """Initialize the exception."""
        super().__init__(message, line_text, line_number)


class SectionException(Exception):
    """The base class of all SECTION memory exceptions."""

    def __init__(self, message, line_text="", line_number=-1):
        """Initialize the exception."""
        super().__init__(message, line_text, line_number)


class SectionDeclarationError(SectionException):
    """An exception that is thrown if the SECTION definition is invalid."""

    def __init__(self, message, line_text="", line_number=-1):
        """Initialize the exception."""
        super().__init__(message, line_text, line_number)


class SectionTypeError(SectionException):
    """An exception thrown if the SECTION type is invalid."""

    def __init__(self, message, line_text="", line_number=-1):
        """Initialize the exception."""
        super().__init__(message, line_text, line_number)


class ExpressionException(Exception):
    """A generic exception. Other exceptions are derrived from this."""

    def __init__(self, message):
        """Initiaze the exception with a relevant message."""
        super().__init__(message)


class ExpressionSyntaxError(ExpressionException):
    """Thrown when a numerical or string expression is invalid."""

    _def_msg = "The expression string was not in a valid format."

    def __init__(self, message=_def_msg):
        """Initiaze the exception with a relevant message."""
        super().__init__(message)


class ExpressionTypeError(ExpressionException):
    """Thrown when a numerical or string expression is invalid."""

    _def_msg = "The input value is not an `str` type."

    def __init__(self, message=_def_msg):
        """Initiaze the exception with a relevant message."""
        super().__init__(message)


class ExpressionDescriptorError(ExpressionException):
    """Thrown when a numerical or string expression is invalid."""

    _def_msg = "The expression failed to validate against it's format."

    def __init__(self, message=_def_msg):
        """Initiaze the exception with a relevant message."""
        super().__init__(message)


class UpdateSymbolAddressError(ParserException):
    """Attempt to update the address of a non-addressing Symbol."""

    _def_msg = "Attempt to update the address of a non-addressing Symbol"

    def __init__(self, message=_def_msg, line_text="", line_number=-1):
        """Initialize Exception."""
        super().__init__(message, line_text, line_number)


class DescriptorException(Exception):
    """The base class of all Descriptor exceptions."""

    def __init__(self, message: str):
        """Initialize the base exception."""
        super().__init__(message)


class DescriptorRadixError(DescriptorException):
    """An unsupported base value was specified"""
    _def_msg = "Base can only 2, 8, 10 or 16"

    def __init__(self, message=_def_msg):
        """Initialize Exception."""
        super().__init__(message)


class DescriptorRadixDigitValueError(DescriptorException):
    """An exception when an invalid base character was encountered.

    For example, a HEX (base-16) value of "FH" is invlid since "H" is outside
    of the supported characters (0-9, A-F)"""
    _def_msg = ("A character was used outside of the defined "
                "base numbering character set")

    def __init__(self, message=_def_msg):
        """Initialize the exception."""
        super().__init__(message)


class DescriptorMinMaxValueError(DescriptorException):
    """A value is outside of the descriptor's defined limits."""
    _def_msg = "A value is outside of the min/max limits of this descriptor."

    def __init__(self, message=_def_msg):
        """Initialize Exception."""
        super().__init__(message)


class DescriptorMinMaxLengthError(DescriptorException):
    """A value is outside of the descriptor's defined length."""
    _def_msg = "A value is outside of the min/max length of this descriptor."

    def __init__(self, message=_def_msg):
        """Initialize Exception."""
        super().__init__(message)


class DefineException(ParserException):
    """Generic DEF error."""

    _def_msg = "Unknown generic DEF error."

    def __init__(self, message=_def_msg, line_text="", line_number=-1):
        """Initialize Exception."""
        super().__init__(message, line_text, line_number)


class DefineExpressionError(DefineException):
    """A DEF Expression error."""

    _def_msg = "The provided expression was not valid."

    def __init__(self, message=_def_msg, line_text="", line_number=-1):
        """Initialize Exception."""
        super().__init__(message, line_text, line_number)


class DefineSymbolError(DefineException):
    """A DEF Symbol error."""

    _def_msg = "The Symbol in the DEF statement is not valid."

    def __init__(self, message=_def_msg, line_text="", line_number=-1):
        """Initialize Exception."""
        super().__init__(message, line_text, line_number)


class DefineAssignmentError(DefineException):
    """A DEF Assignment error."""

    _def_msg = "The assignment of the symbol to the expression is invalid."

    def __init__(self, message=_def_msg, line_text="", line_number=-1):
        """Initialize Exception."""
        super().__init__(message, line_text, line_number)


class StorageException(ParserException):
    """Generic Storage error."""

    _def_msg = "Unknown generic Storage error."

    def __init__(self, message=_def_msg, line_text="", line_number=-1):
        """Initialize Exception."""
        super().__init__(message, line_text, line_number)


class StorageValueError(StorageException):
    """Storage value is out of range of its defined limits."""

    _def_msg = "The storage value is out of range of a pre-defined min/max."

    def __init__(self, message=_def_msg, line_text="", line_number=-1):
        """Initialize the exception."""
        super().__init__(message, line_text, line_number)


InvalidLabelName = DescriptorException
InvalidSymbolName = ExpressionSyntaxError
InvalidSymbolScope = ExpressionSyntaxError
EquateSymbolError = ExpressionSyntaxError
EquateExpressionError = ExpressionSyntaxError
