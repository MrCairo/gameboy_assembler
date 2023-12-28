
class _OldToken:
    """Object that encapsulates pieces of parsed data (lexemes).

    This object is an accessor class to the underlying data structure that
    represents a line of source code text. The Token class itself doesn't
    parse, but it is used to store the divided up pieces without resorting to
    an untyped dictionary.
    """

    __slots__ = [value_t, type_t, datum_t]

    def __init__(self):
        """Initialize an empty token."""
        self._tok = OrderedDict()

    def __repr__(self) -> str:
        """Return representation on how this object can be built."""
        subs = [self.value]
        _next = self.next
        while _next is not None:
            subs.append(_next.value)
            _next = _next.next
        desc = f"Token.from_elements({subs})"
        return desc

    def __str__(self) -> str:
        """Return a human readable string for this object."""
        desc = f"type: {self.type}, val: '{self.value}', "
        desc += f"dat: {type(self.datum)}"
        if self.next:
            desc += f"\n{self.next.__str__()}"
        return desc

    @classmethod
    def from_elements(cls, elements: list) -> Token:
        """Create a new token from a list of elements.

        Parameters
        ----------
        elements : list
            A list of elements that are to assigned to the token
        """
        if not elements:
            raise ValueError("List of elements missing.")
        return TokenFactory(elements).token

    # Helper functions
    def copy(self) -> Token:
        """Return a copy of this token sans next.

        This is preferred over the copy(obj) or deepcopy(obj) functions since
        we only want to copy the value, type, and datum. The next value is not
        copied since it will result in a recusive copy which we don't want.
        """
        new_tok = Token()
        new_tok.value = self.value
        new_tok.type = self.type
        new_tok.datum = self.datum
        return new_tok

    @property
    def value(self) -> str:
        """Return the token value as a string, or None if empty."""
        return self.lexeme(value_t)

    @property
    def next(self) -> Optional[Token]:
        """Return the directive value as a string, or None if empty."""
        return self.lexeme(next_t)

    @property
    def type(self) -> Optional[str]:
        """Return the directive value as a string, or None if empty."""
        return self.lexeme(type_t)

    @property
    def datum(self) -> Optional[Symbol, dict]:
        """Return the datum associated with the token, if any."""
        return self.lexeme(datum_t)

    #
    # Primary getter and setter for the token.
    #
    def lexeme(self, key: str) -> \
            str | dict | Token | Symbol | Expression | None:
        """Return an entry from the Token dict if present."""
        return self._tok.get(key, None)

    def set_lexeme(self, key: str,
                   value: str | dict | Token | Symbol | Expression) -> bool:
        """Assign a value to a new or existing lexeme in the Token.

        Parameters
        ----------
        key : str
            The key name (i.e. TOK_T)

        value : TokenArgType
            The value to assign to the token key.
        """
        if key not in LEXEMES:
            return False
        if key == arguments_t:
            args = [x for idx, x in enumerate(value)]
            # args = {f'arg{idx:02d}': x for idx, x in enumerate(value)}
            self._tok[key] = args
        else:
            self._tok[key] = value
        return True

    #
    # --------========[ Private methods ]========-------- #
    def _assign_old(self, pieces: list):
        """Assign list values to the Token."""
        if pieces is None or len(pieces) == 0:
            return
        try:
            if len(pieces[0]) == 1 and pieces[0] in "\"'([{}])":
                self._assign_values(pieces, TokenType.PUNCTUATOR)
            elif pieces[0] in DIRECTIVES:
                self._assign_values(pieces, TokenType.DIRECTIVE)
            elif pieces[0] in MEMORY_BLOCKS:
                self._assign_values(pieces, TokenType.MEMORY_BLOCK)
            elif Expression.has_valid_prefix(pieces[0]):
                self._assign_values(pieces, TokenType.EXPRESSION)
            elif SymbolUtils.is_valid_symbol(pieces[0]):
                self._assign_values(pieces, TokenType.SYMBOL)
            elif IS().is_mnemonic(pieces[0]):
                self._assign_values(pieces, TokenType.KEYWORD)
            else:
                self._assign_values(pieces, TokenType.LITERAL)
        except (InvalidSymbolName, InvalidSymbolScope) as err:
            self._assign_invalid([err] + pieces)

    def _assign_invalid(self, elements):
        self.set_lexeme(type_t, TokenType.INVALID)
        self.set_lexeme(value_t, elements)

    def _assign_values(self, elements, tok_type: TokenType) -> bool:
        if elements is None:
            return False
        self.set_lexeme(value_t, elements[0])
        self.set_lexeme(type_t, tok_type)
        if len(elements) > 1:
            self._assign_next(elements[1:])

        match tok_type:
            case TokenType.KEYWORD:
                self._assign_instruction(elements)
            case TokenType.SYMBOL:
                self._assign_symbol(elements[0])
            case TokenType.EXPRESSION:
                self._assign_expression(elements[0])
        return True

    def _assign_instruction(self, elements: list):
        mnemonic = elements[0]
        ins = IS().instruction_from_mnemonic(mnemonic.upper())
        self.set_lexeme(datum_t, ins)

    def _assign_symbol(self, name: str):
        sym = Symbol(name, 0x00)
        self.set_lexeme(datum_t, sym)

    def _assign_expression(self, expr: str):
        self.set_lexeme(datum_t, Expression(expr))

    def _assign_next(self, elements) -> bool:
        tok = Token.from_elements(elements)
        self.set_lexeme(next_t, tok)
        return True

    # --------========[ End of Token class ]========-------- #
