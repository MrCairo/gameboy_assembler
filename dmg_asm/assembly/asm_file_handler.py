"""File Handler for Assembler related operations."""
from io import open, TextIOWrapper

from ..tokens import Tokenizer, TokenGroup
from ..core.constants import Environment
from .asm_token_resolver import AsmTokenResolver

INCL_PREFIX = "INCLUDE "


class AsmFileHandler:
    """File Handler during assembly phase."""

    # It is the intention that this class remain local to the 'assembly'
    # module.

    _env: Environment
    _resolver: AsmTokenResolver

    def __new__(cls, env: Environment):
        """Create a new instance of this class."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(AsmFileHandler, cls).__new__(cls)
            cls.instance._env = env
            cls.instance._resolver = AsmTokenResolver(env)
        return cls.instance

    def process_file(self, filename: str) -> None:
        """Process the contents of the file through the assembler."""
        if filename is None or len(filename) == 0:
            return
        if filename.startswith(self._env.project_dir):
            fq_name = filename
        else:
            fq_name = f"{self._env.project_dir}/{filename}"
        line: str | None = ""
        with open(fq_name, "rt", encoding="utf-8") as filestream:
            while line is not None:
                line = self.read_line(filestream)
                if line is not None and isinstance(line, str):
                    if len(line) == 0:
                        continue
                    if line.upper().startswith("INCLUDE "):
                        incl_filename = self.get_include_filename(line)
                        if incl_filename:
                            print(f"Going to process file {incl_filename}")
                            # self.process_file(incl_filename)
                        continue
                    tokens: TokenGroup = Tokenizer().tokenize_string(line)
                    self._resolver.process_tokens(tokens)
                    print(f"{line} ** OK")
                else:
                    break

    def read_line(self, stream: TextIOWrapper) -> str | None:
        """Read one line from the data source.

        Line is a sequence of bytes ending with CR.
        """
        line = stream.readline()
        if len(line) == 0:
            return None
        preread = self.drop_comments(line)
        if preread is not None and len(preread) > 1:
            while preread[-1] == "\\":  # Line continuation
                preread = preread.strip(" \\")  # Space here is intentional
                line = stream.readline()
                if len(line):
                    line = line.strip()
                    preread += line
        return preread

    def get_include_filename(self, code_line: str) -> str | None:
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

    def drop_comments(self, line_of_text) -> str | None:
        """Remove any comments that are part of the line_of_text."""
        if line_of_text is not None:
            return line_of_text.strip().split(";")[0]
        return None
