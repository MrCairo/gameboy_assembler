"""Manages the storage of things going in a Section.

The main intention of this class is to not only provide a place to store
data, but also to ensure that data doesn't exceed the section bounds and can
be retrieved by label, symbol, address, etc."""

from ..directives import Section


class SectionBuilder:
    """A class to maintain code within a single Section."""

    _stack: bytearray
    _section: Section
    _remaining_space: int

    def __init__(self, section: Section):
        """Initialize the object."""
        self._stack = bytearray()
        self._section = section
        self._remaining_space = section.memory_block

    def __str__(self):
        return ""

    def __repr__(self):
        return f"SectionBuilder(section: {self._section})"

    def append_code(self,
