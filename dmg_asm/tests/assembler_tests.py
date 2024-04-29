import unittest
import os

from ..core.constants import Environment
from ..assembly import Assembler


class AssemblerUnitTests(unittest.TestCase):
    """Test assmbling of a source file."""

    def test_assemble_file_with_includes(self):
        """Compile a file."""
        proj = f"{os.environ['PROJECT_DIR']}/dmg_asm/tests/resources"
        env = Environment(project_dir=proj,
                          include_dir="includes",
                          source_dir="")
        Assembler().environment = env
        Assembler().build("test_source.z80")
