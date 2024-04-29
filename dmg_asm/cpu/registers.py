# -*- coding: utf-8 -*-
"""
Class that represent the GBZ80 registers.
"""


class Registers:
    """Class that represents and validates the GBZ80 registers."""

    __slots__ = ('all_registers', 'working_registers')

    def __new__(cls):
        """Implement a singleton by returning the existing or new instance."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Registers, cls).__new__(cls)
            cls.instance.all_registers = ['B', 'C', 'BC', 'D', 'E', 'DE', 'H',
                                          'L', 'HL', 'A', 'F', 'PC', 'SP']
            cls.instance.working_registers = ['B', 'C', 'D', 'E', 'H', 'L',
                                              '(HL)', 'A']

        return cls.instance

    def is_valid_register(self, register):
        """Return True/False if the register provided is a known register."""
        if register:
            # _special = ["(HL+)", "(HL-)", "SP+"]
            clean = register.strip("() +-")
            if len(clean):
                return clean in self.all_registers
        return False
