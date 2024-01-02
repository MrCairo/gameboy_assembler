#
#
from typing import Dict
from ..core.constants import DIR_T, TOK_T, BAD_T, MULT_T


class LexicalNode:
    """
    LexicalNode is a specialized object or more like a pseudo dictionary.  The
    LexicalNode contains only a directive string and a token dictionary.  As a
    result, this object ONLY allows the keys of DIR_T and TOK_T to be read
    Additionally, the value of DIR_T must be of type str (or None) and TOK_T
    must be of type dict (or None).

    As mentioned above, the LexicalNode has a __getitem()__ which means
    that it is possible to use the lexical node like

        node = LexicalNode(directive, tokens)
        print(node[TOK_T])
        print(node[DIR_T])
        node[TOK_T] = "Test"      # Raises an IndexError. Set is not possible

    Parameters:
    - directive (str): The type of construct that the TOK_T value contains
            which can be an STOR, INST, LBL, MULT_T, or None. This is no check
            for the value of the directive other than it has to be a str or
            None.
    - tokens (list, dict): A dict object that contains the tokenized values of
            a single line of source code parsed by the LexicalAnalyzer. This
            is generally an array but can also be a dictionary object. If the
            token is an array, it is also possible that the tokens are an
            array of LexicalNodes. This is also valid.
    """

    def __init__(self, directive: str = None, tokens=None):
        # The intention is to make this object immutable but we're not using
        # the new 3.7 feature for a frozen data class.
        # Be a good neighbor and don't access underscore variables outside of
        # the scope of this class :)
        self._data = {DIR_T: directive, TOK_T: tokens}
        if not LexicalNode.is_valid_node(self):
            raise TypeError(self._data)

    def __getitem__(self, key):
        if key in [TOK_T, DIR_T]:
            return self._data[key]
        raise IndexError(key)

    def __contains__(self, key) -> bool:
        if key in [DIR_T, TOK_T]:
            return key in self._data.keys()
        return False

    #
    # Should this be a mutable class? For now, NO and we try our best to do
    # that here.
    #
    def __setitem__(self, key, value):
        raise IndexError

    def __repr__(self):
        desc = f"{self._repr_of_instance()}\n"
        # Check for embedded LexicalNode
        tokens = self.token()
        if tokens is not None and type(tokens) is list:
            if len(tokens) and tokens[0] is dict:
                if LexicalNode.is_valid_node(tokens[0]):
                    desc += ">>> inner node >>>\n"
                    desc += f">>> {item._repr_of_instance()}\n"
                else:
                    desc += ">> INVALID LexicalNode >>\n"
                    return desc
        return desc

    def __str__(self):
        desc = "\n LexicalNode: \n"
        desc += f"    directive = {self.directive()}\n"
        desc += f"    tokens = {self.token()}"
        if self._data[TOK_T] is not None:
            item = self._data[TOK_T]
            if DIR_T in item and TOK_T in item:
                x = LexicalNode(item[DIR_T], item[TOK_T])
                desc += "\n>>> Inner LexicalNode\n" + x.__str__()
        return desc

    # def __setitem__(self, key, value):
    #     if key == DIR_T:
    #         if type(value) is str or value is None:
    #             self._data[DIR_T] = value
    #         raise TypeError(value)
    #     elif key == TOK_T:
    #         if type(value) is dict or value is None:
    #             self._data[TOK_T] = value
    #         raise TypeError(value)
    #     else:
    #         raise IndexError(key)

    def directive(self) -> str:
        """Return the current DIR_T value."""
        """This value can also be accessed as 'variable[DIR_T]'. It is possible
        for this value to be None."""
        return self._data[DIR_T]

    def token(self):
        """Return the current TOK_T value."""
        """This value can also be accessed as 'variable[TOK_T]'. It is possible
        for this value to be None."""
        return self._data[TOK_T]

    def value(self) -> Dict:
        """Return the current LexicalNode as a raw dictionary."""
        """Please note that this is a copy of the LexicanNode and not a
        reference to the actual values."""
        return {DIR_T: self[DIR_T], TOK_T: self[TOK_T]}

    def _repr_of_instance(self) -> str:
        return f"LexicalNode(\"{self._data[DIR_T]}\", \"{self._data[TOK_T]}\")"

    @classmethod
    def is_valid_node(cls, node) -> bool:
        """Return True if the node is valid. False otherwise."""
        valid = type(node) is LexicalNode
        if valid:
            valid = TOK_T in node and DIR_T in node
        if valid:
            valid = node[DIR_T] is not BAD_T
        if valid and node[DIR_T] is None:
            valid = node[DIR_T] is None and node[TOK_T] is None
        if valid:
            valid = DIR_T in node and TOK_T in node
        if valid and node[TOK_T] is not None:
            valid = (type(node[TOK_T]) is list or type(node[TOK_T]) is dict or
                     type(node[TOK_T]) is str or type(node[TOK_T] is LexicalNode))
        if valid and node[DIR_T] is MULT_T:
            if type(node[TOK_T]) is LexicalNode:
                newNode = node[TOK_T]
                valid = LexicalNode.is_valid_node(newNode)
        return valid
