# diff2test/models.py
from dataclasses import dataclass


@dataclass
class DiffInfo:
    """
    Holds information about a single file's diff.
    """

    file_path: str
    diff_content: str
    # Future extensions could include:
    # change_type: str # e.g., "A" (added), "M" (modified), "D" (deleted)
    # commit_hash: str


@dataclass
class AIConfig:
    project_id: str
    region: str
    model_name: str = "gemini-2.0-flash"  # You can change this default
