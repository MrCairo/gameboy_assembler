# -*- coding: utf-8 -*-
"""
Class that represent the GBZ80 registers.
"""

from singleton_decorator import singleton

@singleton
class Registers():
    """Class that represents and validates the GBZ80 registers."""
    def __init__(self):
        self._all_registers = [
            'B', 'C', 'BC', 'D', 'E', 'DE', 'H', 'L', 'HL', 'A', 'F', 'PC',
            'SP']
        self._working_registers = ['B', 'C', 'D', 'E', 'H', 'L', '(HL)', 'A']

    def all_registers(self):
        """Returns an array of all registers. """
        return self._all_registers

    def working_registers(self):
        """An array of GBZ80 working registers."""
        return self._working_registers

    def is_valid_register(self, register):
        """Returns True/False if the register provided is a known register."""
        if register:
            _special = ["(HL+)", "(HL-)", "SP+"]
            clean = register.strip("() +-")
            if len(clean):
                return clean in self._all_registers
        return False
