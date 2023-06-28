from pathlib import Path
import os


def get_root_directory() -> Path:
    return Path(os.path.dirname(os.path.realpath(__file__)))
