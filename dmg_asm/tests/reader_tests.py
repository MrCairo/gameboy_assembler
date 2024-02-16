"""Test the Reader Class."""

import os
import unittest

from ..core.reader import Reader, FileReader, BufferReader
from ..tokens import TokenGroup, Tokenizer


class CoreReaderTests(unittest.TestCase):
    """Test the Reader class for opening and reading files and buffers."""

    def test_can_open_and_read_file(self):
        """Test if a file can be opened and read."""

        dir_path = os.path.dirname(os.path.realpath(__file__))
        reader = FileReader(f"{dir_path}/resources/includes/constants.z80")
        self.assertIsNotNone(reader)
        lines_read: int = 0
        line = reader.read_line()
        while not reader.is_eof():
            self.assertIsNotNone(line)
            lines_read += 1
            line = reader.read_line()
        reader.close()
        print(f"{lines_read} lines read from file")
        self.assertTrue(lines_read > 0)
