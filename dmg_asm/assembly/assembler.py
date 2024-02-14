"""Compile GameBoy Z80 Source and pass it to the gbz80 Assember."""

from io import open, TextIOWrapper

from ..tokens import Tokenizer, TokenGroup
from ..core.constants import Environment
from .asm_utils import AsmUtils


INCL_PREFIX = "INCLUDE "


class Assembler:
    """Compiles GBZ80 Source into a form that the Assember can use."""

    _env: Environment
    _utils: AsmUtils

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Assembler, cls).__new__(cls)
            cls.instance._env = None
            cls.instance._utils = None
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
        self._utils = AsmUtils(self._env)

    def build(self, filename: str) -> bool:
        """Assemble a GB Z80 source file into binary."""
        if self._env is None:
            msg = "An environment must be set before calling 'build'."
            raise ValueError(msg)
        self._process_file(filename)
        return True

    def save(self):
        """Save the assembled code to the output file.

        The output file is specified in the environment object. If None or
        blank, the output filename will default to "game.data"."""

    # -----[ Private methods ]----------------------------------------

    def _process_file(self, filename: str) -> None:
        """Process the contents of the file through the assembler."""
        if filename is None or len(filename) == 0:
            return
        if filename.startswith(self._env.project_dir):
            fq_name = filename
        else:
            fq_name = f"{self._env.project_dir}/{filename}"
        line: str = ""
        with open(fq_name, "rt", encoding="utf-8") as filestream:
            while line is not None:
                line = self._read_line(filestream)
                if line is not None and isinstance(line, str):
                    if len(line) == 0:
                        continue
                    #
                    # TODO: What about INCBIN?
                    #
                    if line.upper().startswith("INCLUDE "):
                        self._process_file(self._get_include_filename(line))
                        continue
                    tokens: TokenGroup = Tokenizer().tokenize_string(line)
                    print(line)
                    self._utils.process_tokens(tokens)
                else:
                    break
        # end of function

    def _read_line(self, stream: TextIOWrapper) -> str:
        """Reads one line from the data source.
        Line is a sequence of bytes ending with \n."""
        line = stream.readline()
        if len(line) == 0:
            return None
        preread = self._drop_comments(line)
        if preread is not None and len(preread) > 1:
            while preread[-1] == "\\":  # Line continuation
                preread = preread.strip(" \\")  # Space here is intentional
                line = stream.readline()
                if len(line):
                    line = line.strip()
                    preread += line
        return preread

    def _get_include_filename(self, code_line: str) -> str | None:
        """Return the fully-qualified include file from code_line."""
        fq_file = ""
        if not code_line.upper().startswith(INCL_PREFIX):
            return None
        file_part = code_line[len(INCL_PREFIX):]
        inc_file = file_part.strip(" '\"")
        if len(inc_file) == 0:
            return None
        if inc_file.startswith("/"):
            return None  # INCLUDE must be relative to the environment
        if len(self._env.include_dir):
            fq_file = self._env.include_dir
        return f"{self._env.project_dir}/{fq_file}/{inc_file}"

    def _drop_comments(self, line_of_text) -> str:
        if line_of_text is not None:
            return line_of_text.strip().split(";")[0]
        return None
