"The files and paths that are used by the assembler."

import os
from dataclasses import dataclass


@dataclass
class Environment:
    """A set of values that the compiler/assembler uses to operate."""

    project_dir: str = None  # Absolute path to the project
    source_dir: str = None   # Source directory relative to project_dir
    include_dir: str = None  # Include source relative to project_dir

    def __init__(self, project_dir: str = os.getcwd(),
                 source_dir: str = None,
                 include_dir: str = None):
        """Initialize the object."""
        if project_dir is None or len(project_dir) == 0:
            self.project_dir = os.getcwd()
        else:
            self.project_dir = project_dir
        self.source_dir = source_dir if source_dir else ""
        self.include_dir = include_dir if include_dir else ""
