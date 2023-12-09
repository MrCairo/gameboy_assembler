"""Classes that convert text into Tokens."""

from typing import Optional
from .token_group import TokenGroup
from .token import Token


#
# The Tokenizer simply breaks up a line of text into a dictionary. The
# dictionary starts off with a DIRECTIVE entry which identifies what the root
# command of the input line is. If the directive contains other directives, an
# additional DIRECTIVE entry is included.
#
# ------------------------------------------------------------------------------
#
# It's important to note that tokenizing a line of text isn't the same thing as
# validating the conents. While the actual basic items are identified -
# Directive, instructions, or symbols - the parameters that appear after the
# directive are not checked against syntax.
#
# ------------------------------------------------------------------------------
#


class Tokenizer:
    """Create and manage groups tokens.

    Tokens are automatically added to the group created from either a line of
    text or an array of individual elements.
    """

    def __init__(self):
        """Initialze the Tokenizer obect."""
        self.clear()

    def clear(self):
        """Reset (clear) the current token group."""
        self._group = TokenGroup()

    @property
    def token_group(self) -> TokenGroup:
        """Return the TokenGroup token store."""
        return self._group

    def tokenize_string(self, line_of_text: str) -> Optional[TokenGroup]:
        """Convert text to a token and add it to the token group."""
        elements = self._elements_from_string(line_of_text)
        if elements:
            self.tokenize_elements(elements)
        return self._group

    def tokenize_elements(self, elements: list) -> Optional[TokenGroup]:
        """Convert elements to a token and add it to the token group."""
        try:
            token = Token.from_elements(elements)
        except TypeError:
            return None
        self._group.add(token)
        remn = token.remainder
        if remn:
            self.tokenize_elements(remn)

        # Add the token to the group. If there is remnant token data
        # go into that remnant token and add it to the group as well.
        # Continue to add remnant tokens until there are none. Generally,
        # there should only be at the most one remnant token but the
        # TokenGroup class is meant to handle as many as needed.
        # rmn_token = token.remainder
        # while rmn_token is not None:
        #     self._group.add(rmn_token)
        #     rmn_token = rmn_token.remainder
        return self._group

    def list_to_dict(self, arr: list) -> dict:
        """Convert a list to a dictionary with keys like argNN."""
        return {f"arg{idx:02d}": x for idx, x in enumerate(arr)}

    def clean_text(self, line_of_text: str) -> str:
        """Remove comments, leading/trailing spaces, and explode brackets."""
        cleaned = self._drop_comments(line_of_text)
        if len(cleaned) > 0:
            cleaned = self._explode_brackets(cleaned)
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
        elements = [x for x in clean.split(" ") if x != ""]
        # Starting/ending Commas are irrelevant so ignore them
        elements = [s.strip(",") for s in elements]
        elements = [x for x in elements if len(x)]

        return elements

    def _explode_brackets(self, text: str) -> str:
        """Return a string with brackets exploded for splitting.

        There are three types of brackets recognized:
            Round brackets: ()
            Square brackets: []
            Curly brackets: {}
        Also, the double quote and single quote values are also
        added to this as then also are used to enclose data.
        """
        brackets = "\"'([{}])"
        exploded = text
        if any(char in text for char in brackets):
            for char in brackets:
                exploded = exploded.replace(char, f" {char} ")
        return exploded

        # --------========[ End of Tokenizer class ]========-------- #
