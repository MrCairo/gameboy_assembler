"""
"""
from ..core.exception import Error


class LexerTokens:
    """
    A data class that stores the instruction tokens and provides easy
    access to the token values.
    """

    def __init__(self, tokens: dict) -> None:
        self._top = tokens if tokens else {}
        self._tok = {} if "tok" not in tokens else tokens
        self._extra = {}

    def tokens(self):
        """
        The raw tokens created by the lexer. It still may have values
        even if the instruction parsed was invalid.
        """
        return None if "tok" not in self._tok else self._tok["tok"]

    def opcode(self) -> str:
        """
        Returns the opcode (mnemonic) from the tokens
        """
        return self._exploded_val("opcode")

    def operands(self) -> [str]:
        """
        Returns the operands from the tokens
        """
        return self._exploded_val("operands")

    def definition(self) -> dict:
        """
        Returns the instruction definition as defined in the
        InstructionSet
        """
        ins_def = None if "ins_def" not in self._tok else self._tok["ins_def"]
        return ins_def

    def extra(self) -> dict:
        return self._extra

    def set_extra(self, key, value):
        self._extra[key] = value

    def _exploded_val(self, key):
        tok = self.tokens()
        if not tok:
            return None
        ops = None if key not in tok else tok[key]
        return ops

    # --------========[ End of LexerTokens class ]========-------- #


class LexerResults:
    """
    Encapsulates a result from parsing an instruction. This class
    stores the bytearray of the parsed instruction or an error string.
    A Lexeresult object with out the 'data; property being set indicates
    a failed parse. In this case the '*error' properties should contain the
    error information (via the Error object). All methods return None if
    it's value doesn't exist either due to no data present.
    """
    _raw: dict = {}
    _tok: LexerTokens = {}

    def __init__(self, raw_results: dict, tokens: LexerTokens) -> None:
        self._raw = {} if raw_results is None else raw_results
        self._tok = {} if tokens is None else tokens

    def lexer_tokens(self) -> LexerTokens:
        """
        The tokenized values of the parsed instruction. The presense of tokens
        does NOT indicate a successful parse of the instruction.
        """
        return self._tok

    def addr(self) -> str:
        """
        Represents the opcode value of the instruction as hex string.
        Additional operand data does not appear here but instead
        appears in binary form via the binary() method or in text
        via the operand1() or operand2() methods.
        """
        return self._if_found("addr")

    def binary(self) -> bytes:
        """
        The binary representation of the parsed instruction.
        """
        return self._if_found("bytes")

    def cpu_cycles(self) -> list:
        """
        Informational only data that represents the number of CPU Cycles that
        the instruction takes.
        """
        return self._if_found("cycles")

    def flags(self) -> list:
        """
        An array of with the values of the Z, N, H, C CPU flags in that order.
        Z = Zero flag. A 'Z' indicates that the instruction can result in a
            zero value.
        N = Add/Sub flag. N = 1 if the previous operation was a subtract
        H = Half Cary flag. H = 1 if the add or subtract operation produced a
            carry into or borrow' from bit 4 of the accumulator.
        C = Carry/link flag C = 1 if the operltlon produced a carry from the
            MSB of the operand or result.
        - = Flag is unaffected by the operation.
        """
        f = ['-', '-', '-', '-']
        if "flags" in self._raw:
            for (idx, val) in enumerate(self._raw['flags'], start=0):
                if idx < 4:
                    f[idx] = val
        return f

    def length(self) -> int:
        """
        The length in bytes of the instruction. This is the opcode plus
        value-based operands if present.
        """
        return self._if_found("length")

    def mnemonic(self) -> str:
        """ The mnemonic (or opcode) of the instruction. """
        return self._if_found("mnemonic")

    def mnemonic_error(self) -> Error:
        """ The error if the mnemonic was invalid. """
        return self._if_found("mnemonic_error")

    def operand1(self) -> str:
        """ The first operand if present. """
        return self._if_found("operand1")

    def operand2(self) -> str:
        """ The second operand if present. """
        return self._if_found("operand2")

    def operand1_error(self) -> Error:
        """
        Contains the error found when processing operand1. A None
        indicates that there is no error.
        """
        return self._if_found("operand1_error")

    def clear_operand1_error(self) -> None:
        """
        Clears any operand1 error value. This is typically used if the
        operand was originally an error due to an unresolved label that
        gets resolved after this object was created.
        """
        if self._if_found("operand1_error"):
            del self._raw["operand1_error"]

    def operand2_error(self) -> Error:
        """
        Contains the error found when processing operand2. A None
        indicates that there is no error.
        """
        return self._if_found("operand2_error")

    def clear_operand2_error(self) -> None:
        """
        Clears any operand2 error value. This is typically used if the
        operand was originally an error due to an unresolved label that
        gets resolved after this object was created.
        """
        if self._if_found("operand2_error"):
            del self._raw["operand2_error"]

    def placeholder(self) -> str:
        """
        The placeholder found and processed in the instruction.
        A placeholder can be one of the following values:
        d8  = immediate 8 bit data.
        d16 = immediate 16 bit data.
        a8  = 8 bit unsigned data, which are added to $FF00 for certain
              instructions (replacement for missing IN and OUT instructions)
        a16 = a 16 bit address
        r8  = 8 bit signed data, which are added to program counter
        """
        return self._if_found("placeholder")

    def extra(self) -> dict:
        """
        Returns a list of instruction/parsed specific data. The data are
        completely optional and provides no indication if the instruction
        is valid or not.
        """

    def unresolved(self) -> str:
        """
        Returns any value that is/was considered unresolved when the
        instruction was initially parsed.
        """
        return self._if_found("unresolved")

    def is_valid(self):
        """
        Returns true if operand1 or operand2 contains an error.
        """
        test = self.mnemonic_error() is None and \
            self.operand1_error() is None and \
            self.operand2_error() is None
        return test

    def _if_found(self, key):
        return None if key not in self._raw else self._raw[key]

    # --------========[ End of LexerResults class ]========-------- #
