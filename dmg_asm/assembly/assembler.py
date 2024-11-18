"""Compile GameBoy Z80 Source and pass it to the gbz80 Assember."""

from ..core.environment import Environment
from .asm_token_resolver import AsmTokenResolver
from .asm_file_handler import AsmFileHandler


INCL_PREFIX = "INCLUDE "


class Assembler:
    """Compiles GBZ80 Source into a form that the Assembler can use."""

    _env: Environment
    _resolver: AsmTokenResolver
    _fhandler: AsmFileHandler

    def __new__(cls):
        """Create a new instance of this class."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Assembler, cls).__new__(cls)
            cls.instance._env = None
            cls.instance._resolver = None
        return cls.instance

    @property
    def environment(self) -> Environment:
        """Return the Environment object."""
        return self._env

    @environment.setter
    def environment(self, new_value: Environment):
        if new_value is None or not isinstance(new_value, Environment):
            msg = "'environment' can only be assigned an Environment object."
            raise ValueError(msg)
        self._env = new_value
        self._resolver = AsmTokenResolver(self._env)
        self._fhandler = AsmFileHandler(self._env)

    def build(self, filename: str) -> bool:
        """Assemble a GB Z80 source file into binary."""
        if self._env is None:
            msg = "An environment must be set before calling 'build'."
            raise ValueError(msg)
        self._fhandler.process_file(filename)
        return True

    def save(self):
        """Save the assembled code to the output file.

        The output file is specified in the environment object. If None or
        blank, the output filename will default to "game.data".
        """

    # -----[ Private methods ]----------------------------------------
