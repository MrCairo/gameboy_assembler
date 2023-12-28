"""
Basic stream readers.
"""
import locale
from typing import Optional


class Reader:
    """
    Main subclass for the file readers. Not meant to be used directly
    rather used as a base class for polymorphic behavior.
    """

    def __init__(self, strip_comments=False):
        self._strip_comments: bool = strip_comments
        self._line: str = None
        self._eof: bool = False
        self._read_position: int = 0

    @property
    def line(self) -> str:
        """Return the last line read from the stream."""
        return self._line

    def read_line(self) -> str:
        """Read the next line in the stream."""
        if self._strip_comments is True:
            self.strip_comment()

    def get_position(self):
        """Return the current read position"""

    def set_position(self, position):
        """Set the current read position"""

    def filename(self) -> str:
        """Return the filename of the file being read (if available)"""

    def is_eof(self) -> bool:
        """Return true if the reader is at the end of the stream."""
        return self._eof

    def strip_comment(self):
        """Strip any comment in the currently read line."""
        # A "*" in the first column means the entire line is a comment
        if self._line[0] == "*":
            self._line = ""
            return
        cleaned = self._line.split(";")
        self._line = cleaned[0]


# end of class Reader


class BufferReader(Reader):
    """
    A Reader object that takes in a buffer and performs Reader operations
    on that buffer. An optional line_delimiter maybe specified which
    represents the EOL or end of line. By default, this value is '\\n'.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, buffer, line_delimiter="\n",
                 debug=False, strip_comments=False):
        super().__init__(strip_comments=strip_comments)
        self._debug = debug
        self._buffer = buffer
        self._len = len(buffer)
        self._delimiter = line_delimiter
        self._dlen = len(self._delimiter)

    def read_line(self) -> str:
        """Get the next line from the file stream."""
        _preread = self._readline()

        # Line continuation
        while _preread is not None:
            if len(_preread) > 1 and _preread[-1] == "\\":
                _preread = _preread[0:-1]
                _preread += self._readline().strip()
            else:
                break

        self._line = _preread
        return self._line

    def get_position(self):
        """Returns the current read position in the file."""
        return self._read_position

    def set_position(self, position) -> bool:
        """Set the position of the reader in the stream."""
        if position in range(0, self._len):  # < self._len and position >= 0:
            self._read_position = position
            self._line = ""
            self._eof = False
            return True
        return False

    def _readline(self) -> Optional[str]:
        """Read the next line from the file stream."""
        _line = None
        if self._read_position < self._len:
            next_delim = self._buffer.find(self._delimiter,
                                           self._read_position)
            if self._debug:
                print(f"Slice = {self._read_position}:{next_delim}")
            if next_delim == -1:
                _line = self._buffer[self._read_position:]
                self._read_position = self._len
                self._eof = True
            else:
                _line = self._buffer[self._read_position:next_delim]
                self._read_position = next_delim + self._dlen
                if self._read_position >= self._len:
                    self._eof = True
            if self._debug:
                print(f"line == '{_line}'")
            return _line
        self._eof = True
        return None

    def filename(self) -> str:
        return "no_filename_required"

# end of class BufferReader


class FileReader (Reader):
    """
    Class to encapsulate the reading of the source as a filesystem file.
    """

    def __init__(self, filename):
        super().__init__()
        self._filename = filename
        self._line = ""
        try:
            with open(filename, encoding=locale.getencoding()) as file:
                self._filestream = file
        except OSError:
            self._eof = True
            print(f"Could not open the file: {filename}")

    def read_line(self) -> str:
        """Reads one line from the data source.
        Line is a sequence of bytes ending with \n.
        """
        _preread = self._filename.readline()
        if _preread is not None and len(_preread) > 1:
            while _preread[-1] == "\\":  # Line continuation
                _preread = _preread[0:-1]
                line = self._filename.readline()
                if line:
                    _preread.append(line.strip())
        self._line = _preread
        if self._line:
            return self._line

        self._eof = True
        return None

    def get_position(self):
        return self._filestream.tell()

    def set_position(self, position):
        pos = self._filestream.seek(position)
        self._line = ""
        if pos == position:
            self._eof = False
        return pos

    def filename(self) -> str:
        """Returns the string name of the file being read."""
        return self._filename

# end of class FileReader
