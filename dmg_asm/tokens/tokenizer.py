"""Classes that convert text into Tokens."""

from typing import Optional
from .token_group import TokenGroup
from .token import Token, TokenFactory


#
# The Tokenizer simply breaks up a line of text into a dictionary. The
# dictionary starts off with a DIRECTIVE entry which identifies what the root
# command of the input line is. If the directive contains other directives, an
# additional DIRECTIVE entry is included.
#
# ------------------------------------------------------------------------------
#
# It's important to note that tokenizing a line of text isn't the same thing as
# validating the contents. While the actual basic items are identified -
# Directive, instructions, or symbols - the parameters that appear after the
# directive are not checked against any syntax. For example, a token could be
# an expression (i.e. $FF) but there is nothing to validate that the
# expression should have been 16-bit instead of 8-bit. The expression is just
# evaluated as an expression and stored.
#
# ------------------------------------------------------------------------------
#


class Tokenizer:
    """Create and manage groups tokens.

    Tokens are automatically added to the group created from either a line of
    text or an array of individual elements.

    Main funcion:
    tokenize_string(line_of_text: str) -> TokenGroup | None
    """

    def __init__(self):
        """Initialze the Tokenizer obect."""
        self.clear()

    def clear(self):
        """Reset (clear) the current token group."""
        self._group = TokenGroup()

    def tokenize_string(self, line_of_text: str) -> Optional[TokenGroup]:
        """Convert text to a token and add it to the token group."""
        elements = self._elements_from_string(line_of_text)
        if elements:
            self.tokenize_elements(elements)
        return self._group

    def tokenize_elements(self, elements: list) -> Optional[TokenGroup]:
        """Convert elements to a token and add it to the token group."""
        try:
            token: Token = TokenFactory(elements).token
        except TypeError:
            return None
        self._group.add(token.shallow_copy())
        _next_tok = token.next
        while _next_tok is not None:
            self._group.add(_next_tok.shallow_copy())
            _next_tok = _next_tok.next
        # Add the token to the group. If there is remnant token data
        # go into that remnant token and add it to the group as well.
        # Continue to add remnant tokens until there are none. Generally,
        # there should only be at the most one remnant token but the
        # TokenGroup class is meant to handle as many as needed.
        # rmn_token = token.remainder
        # while rmn_token is not None:
        #     self._group.add(next_token)
        #     next_token = next_token.remainder
        return self._group

    def list_to_dict(self, arr: list) -> dict:
        """Convert a list to a dictionary with keys like argNN."""
        return {f"arg{idx:02d}": x for idx, x in enumerate(arr)}

    def clean_text(self, line_of_text: str) -> str:
        """Remove comments, leading/trailing spaces, and explode brackets."""
        cleaned = self._drop_comments(line_of_text)
        if len(cleaned) > 0:
            cleaned = self._explode_delimiters(cleaned)
        return cleaned

    def _drop_comments(self, line_of_text) -> str:
        if line_of_text is not None:
            return line_of_text.strip().split(";")[0]
        return ""

    def _elements_from_string(self, line: str) -> list:
        if len(line) == 0 or line is None:
            return None
        clean = self.clean_text(line)
        if len(clean) == 0:
            return None
        # Break up into pieces and remove any empty elements
        # Starting/ending ',' are irrelevant so ignore them
        elements = [x.strip(",") for x in clean.split(" ") if x != ""]
        # Drop any empty elements
        elements = list(filter(None, elements))
        return elements

    def _explode_delimiters(self, text: str) -> str:
        """Return a string with brackets/+ exploded for splitting.

        There are three types of brackets recognized:
            Round brackets: ()
            Square brackets: []
            Curly brackets: {}
        Also, the double quote and single quote values are also
        added to this as then also are used to enclose data.
        """
        delimiters = "\"'([{}]),+"
        exploded = text
        if any(char in text for char in delimiters):
            for char in delimiters:
                exploded = exploded.replace(char, f" {char} ")
        return exploded

    # --------========[ End of Tokenizer class ]========-------- #
