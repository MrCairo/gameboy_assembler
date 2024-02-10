"""Compiler and Assembler Tests."""

import unittest
import os

from ..compiler import Environment
from ..compiler.compiler import Compiler


class AssemblerUnitTests(unittest.TestCase):
    """Test the Compiler which then tests the Assembler."""

    def test_assemble_file_with_includes(self):
        """Compile a file."""
        proj = f"{os.environ['PROJECT_DIR']}/dmg_asm/tests/resources"
        env = Environment(project_dir=proj,
                          include_dir="",
                          source_dir="")
        Compiler().environment = env
        Compiler().compile("simple_test.z80")
