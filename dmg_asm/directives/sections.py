"""Classes that convert text into Sections."""

# from __future__ import annotations
from typing import Optional
from .section import Section


class Sections:
    """A container to hold Section objects."""

    _store: list

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Sections, cls).__new__(cls)
            cls.instance._store: list = []
        return cls.instance

    def __repr__(self):
        """Represent this object as a printable string."""
        return "Sections()"

    def __str__(self):
        """Format object definition as a printable string."""
        desc = "Sections() = \n"
        for _, sec in enumerate(self._store):
            desc += f"({sec.__str__()})"
        desc += "\n"
        return desc

    def __getitem__(self, index: int):
        """Retrieve an individual token by key."""
        return self.element_at(index)

    def __len__(self):
        """Return the number of keys in the dictionary."""
        return len(self._store)

    def __iter__(self):
        return self._store.__iter__()

    def __reversed__(self):
        return self._store.__reversed__()

    def find_first_index(self, name: str) -> int | None:
        """Return the index in the group that matches the passed value.

        If the value element appears more than once in the group, only the
        first one found is returned."""
        up = name.upper()
        for index, item in enumerate(self._store):
            if item.label.upper() == up:
                return index
        return None

    def push(self, section: Section, replace: bool = False) -> bool:
        """Add a section to the store of sections.

        If the section label name already exists, this function will return a
        False unless 'replace' is set to True in which case the old section is
        replaced with this new one.

        If the section is added (or replaced), this function returns True."""
        if not section:
            raise ValueError("Section cannot be None.")
        if self.find_first_index(section.label):
            if replace:
                self.pop(section.label)
            else:
                return False
        self._store.append(section)
        return True

    def pop(self, name: str) -> Section | None:
        """Remove the first Section found by label name.

        This method will raise a ValueError exception if the section wasn't
        found."""
        if not name:
            raise ValueError("Parameter cannot be None.")
        if not isinstance(name, str):
            raise TypeError("Parameter must be a str object.")
        existing = self.find_first_index(name)
        if existing is None:
            raise ValueError("Section to remove wsan't found.")
        return self._store.pop(existing)

    def clear(self):
        """Removes all stored Section objects. Resets the internal store."""
        self._store.clear()

    def replace(self, section: Section) -> bool:
        """Replace an existing section with the same label name."""
        if not section:
            raise ValueError("Section cannot be None.")
        if not isinstance(section, Section):
            raise TypeError("Parameter must be a Section object.")
        existing = self.find_first_index(section.label)
        if existing is None:
            return False
        self._store[existing] = section
        return True

    def sections(self) -> list:
        """Return a list of Sections in the group."""
        return self._store

    def element_at(self, index: int) -> Section:
        """Return the Section at the 0-based index provided."""
        if 0 <= index < len(self._store):
            return self._store[index]
        raise IndexError
        # raise IndexError("Index out of range")
