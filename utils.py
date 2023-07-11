import os
import re
from functools import wraps
from pathlib import Path
from time import time


def timing(fun):
    """
    Decorator that prints the execution time for the decorated function. A modifed
    version of the one found here: https://stackoverflow.com/questions/1622943/timeit-versus-timing-decorator
    """

    @wraps(fun)
    def wrap(*args, **kw):
        ts = time()
        result = fun(*args, **kw)
        te = time()
        print(f"--- function {fun.__name__} took {te - ts:.3} seconds ---")
        return result

    return wrap


def get_root_directory() -> Path:
    return Path(os.path.dirname(os.path.realpath(__file__)))


def extract_markdown_from_str(text: str) -> str:
    """Extract markdown from a string by removing all lines that don't start with
    -, *, #, or ["""
    lines = text.split("\n")
    markdown_lines = [
        line for line in lines if re.match(r"^(\s*[-*]|\s*#+\s*|\[.*\]\(.*\))", line)
    ]
    return "\n".join(markdown_lines)
