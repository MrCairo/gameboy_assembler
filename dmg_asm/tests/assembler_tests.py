import unittest
import os

from ..compiler import Environment
from ..compiler.compiler import Compiler


class AssemblerUnitTests(unittest.TestCase):

    def test_assemble_file_with_includes(self):
        """Compile a file."""
        proj = f"{os.environ['PROJECT_DIR']}/dmg_asm/tests/resources"
        env = Environment(project_dir=proj,
                          include_dir="includes",
                          source_dir="")
        Compiler().environment = env
        Compiler().compile("test_source.z80")
