"""Classes to handle labels.

A label is similar to a symbol with the following exceptions:
1. A label stores a value whereas a symbol associates an address
2. A label is global in scope whereas a symbol is also private and local.
3. A label doesn't have any special decorator characters (like . or :)
   In fact, a label can only contain alpha/digits and "_" and is validated
   using a LBL_DSC descriptor.
4. In the case of a SECTION directive, a label is optionally defined as a
   string (in quotes). In the case of the EQU or DEF directive, the label is
   not in quotes.

Since a label is more generic in nature it is important that the consumer of
a label only attempts to store TokenType.LITERAL types that have a high
probability of being a label.

example:
  DEF MY_LABEL = 0100     # Label is MY_LABEL
  SECTION "Working", WRAM  # Label is Working

"""

from dataclasses import dataclass
from .descriptor import LBL_DSC
from .expression import Expression


@dataclass
class Label:
    """Represent a single Label name and value."""
    name: LBL_DSC = LBL_DSC
    value: Expression

    def __init__(self, name: str, value: Expression):
        if not isinstance(name, str) or not isinstance(value, Expression):
            raise TypeError("Label name and/or value are not correct types.")
        self.name = name
        self.value = value

    # @property
    # def name(self) -> str:
    #     """Return the label's name."""
    #     return self._name

    # @property
    # def value(self) -> Expression:
    #     """Return the label's Expression value."""
    #     return self._value


class Labels:
    """A specialized dictionary that maintains all symbols.

    Labels is a singleton so it can be allocated (i.e. Labels()) safely
    without the worry of creating a new Labels instance.

    """
    _labels: list

    def __new__(cls):
        """Implement a singleton by returning the existing or new instance."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Labels, cls).__new__(cls)
            cls.instance._labels = []
        return cls.instance

    def __repr__(self):
        """Print the object."""
        desc = ""
        if self._labels:
            for label in self._labels:
                desc = label.__repr__()
        return desc

    def __getitem__(self, index) -> Label:
        """Return Label at index."""
        return self._labels[index]

    def __setitem__(self, index, value) -> None:
        """Set item at index."""
        if not isinstance(value, Label):
            raise TypeError(value)
        self._labels[index] = value

    def __len__(self) -> int:
        return len(self._labels)

    def find(self, name_to_find: str) -> Label | None:
        """Find a label with the specified name.

        'name_to_find' is the name used when creating the Label.
        """
        if len(name_to_find):
            name_to_find = name_to_find.lower()
            found = [x for x in self._labels if x.name.lower() == name_to_find]
            return found[0] if len(found) > 0 else None
        return None

    def value_of(self, name_to_find: str) -> Expression | None:
        """Return the value of a label with the specified name."""
        found = self.find(name_to_find)
        return found.value if found is not None else None

    def push(self, new_label: Label, replace: bool = False) -> bool:
        """Add a new Label object to the list.

        A Label must not have the same name as a label already in the list.
        If this is the case, the 'replace'

        'replace':  Set to True to replace an existing Label with the same
                    name otherwise, the new label with a duplicate name will
                    not be pushed onto the list.

        This function returns True if the Label is pushed onto the list,
        otherwise, this function will return False.
        """
        if not isinstance(new_label, Label):
            raise TypeError(new_label)
        existing = self.find(new_label.name)
        if existing is not None:
            if replace is True:
                existing.value = new_label.value
            return replace
        self._labels.append(new_label)
        return True

    def pop(self) -> Label:
        """Remove a return the Label from the end of the list."""
        if len(self._labels) > 0:
            label = self._labels.pop()
            return label
        return None

    def clear(self):
        """Remove all objects from the list."""
        self._labels.clear()

    # --------========[ End of class ]========-------- #
