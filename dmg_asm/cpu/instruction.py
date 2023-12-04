
"""
Class(es) that implements a Z80/LR35902 instruction and Instruction Set
"""

from .lexer_results import LexerResults
from .lexer_parser import InstructionParser, BasicLexer


class Instruction():
    """ Encapsulates an individual Z80 instruction """

    def __init__(self, node: dict):
        ip = InstructionParser(node)
        self._tokens = ip.tokens()
        self._node = node
        self._lex_results: LexerResults = ip.result()
        self._placeholder_string = None

    @classmethod
    def from_string(cls, text: str):
        """ Builds and Instruction object from plain text. """
        lex = BasicLexer.from_string(text)
        if lex:
            lex.tokenize()
            return cls(lex.tokenized_list()[0])
        return cls({})

    def __str__(self):
        desc = "    " + self.mnemonic()
        unresolved = False
        if self._lex_results.lexer_tokens().operands():
            desc += " " + ',' . \
                join(f"{x}" for x in
                     self._lex_results.lexer_tokens().operands())
            desc += " ;;"
        if self._lex_results:
            if self.machine_code():
                desc += " "
                for byte in self.machine_code():
                    desc += f"{byte:02x} ".upper()
            else:
                if self._lex_results.operand1_error():
                    desc += "  Op1 error = " + \
                        self._lex_results.operand1_error().__repr__()
                    desc += "\n"
                if self._lex_results.operand2_error():
                    desc += "  Op2 error = " + \
                        self._lex_results.operand2_error().__repr__()
                    desc += "\n"
            # if self.placeholder():
            #     desc += "Placeholder = " + self.placeholder()
            #     desc += "\n"
            if self._lex_results.unresolved():
                unresolved = True
                # desc += "Unresolved = " + self._lex_results.unresolved()
                # desc += "\n"
        return desc

    def __repr__(self):
        node = self._node
        if "source_line" in node:
            del node["source_line"]
        if self._lex_results.unresolved():
            node["extra"] = {"unresolved": self._lex_results.unresolved()}
        desc = f"Instruction({self._node})"
        return desc

    def mnemonic(self) -> str:
        """Represents the parsed mnemonic of the Instruction """
        return self._lex_results.mnemonic()

    def operands(self):
        """Returns an array of operands or None if there are no operands """
        return [] if self._tokens.operands() is None else \
            self._tokens.operands()

    def machine_code(self) -> bytearray:
        """
        Returns the binary represent of the parsed instruction.
        This value will be None if the instruction was not parsed
        successfully.
        """
        return self._lex_results.binary()

    def placeholder(self) -> str:
        """
        Returns a custom string that is associated with a placeholder
        used by this object. This property simply allows the consumer
        of the object to associate an arbitrary string to the
        instruction for later retrieval. The property provides no
        other function and has no effect on the validity of the
        instruction object.
        """
        return self._lex_results.placeholder()

    def parse_result(self) -> LexerResults:
        """The result of the parsing of the instruction. This value is
        established at object instantiation."""
        return self._lex_results

    def is_valid(self) -> bool:
        """
        Returns true if the Instruc object is valid. Validity is
        determined on whether the instruction was parsed successfully.
        """
        test = self._lex_results.is_valid()
        return test

    # --------========[ End of Instruction class ]========-------- #


###############################################################################

if __name__ == "__main__":
    ins = Instruction.from_string("LD a, ($ff00)")
    print(ins)

#     ins = Instruction.from_string("JR .RELATIVE")
#     print(ins)

#     ins = Instruction.from_string("LD HL, SP+$17")
#     print(ins)

#     ins = Instruction.from_string("JP NZ, $0010")
#     print(ins)

#     ins = Instruction.from_string("LD ($ff00), a")
#     print(ins)

#     ins = Instruction.from_string("RrCa")
#     print(ins)

#     ins = Instruction.from_string("Add HL, SP")
#     print(ins)

#     ins = Instruction.from_string("LD A, (HL-)")
#     print(ins)

#     ins = Instruction.from_string("ADD SP, $25")
#     print(ins)

#     ins = Instruction.from_string("LD b, c")
#     print(ins)

#     ins = Instruction.from_string("Nop")
#     print(ins)

#     ins = Instruction.from_string("JP (HL)")
#     print(ins)

#     ins = Instruction.from_string("LD A, ($aabb)")
#     print(ins)

#     ins = Instruction.from_string("SET 3, (HL)")
#     print(ins)

#     ins = Instruction.from_string("XOR $ff")
#     print(ins)

#     # Failures
#     ins = Instruction.from_string("JR .RELATIVE")
#     print(ins)

#     ins = Instruction.from_string("NOP A")
#     print(ins)
