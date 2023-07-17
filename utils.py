import os
from functools import wraps
from pathlib import Path
from time import time
import re


def _normalize_markdown_list(markdown_string):
    """
    Function to normalize a markdown string by converting ordered lists to unordered lists and removing unnecessary newlines.

    Args:
        markdown_string (str): The input markdown string to normalize.

    Returns:
        str: The normalized markdown string where all ordered lists have been converted to unordered lists and unnecessary newlines have been removed.
    """

    # Split the markdown string into lines
    lines = markdown_string.split("\n")

    # Initialize an empty list to hold the normalized lines
    normalized_lines = []

    # Iterate over the lines
    for line in lines:
        # Remove leading and trailing whitespace
        line = line.strip()

        # Skip if line is empty
        if not line:
            continue

        # Check if the line is an ordered list item
        if re.match(r"\d+\.", line):
            # Convert the ordered list item to an unordered list item
            line = "- " + re.sub(r"\d+\.\s*", "", line)

        # Append the normalized line to the list of normalized lines
        normalized_lines.append(line)

    # Join the normalized lines back into a string
    normalized_markdown = "\n".join(normalized_lines)

    return normalized_markdown

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


def extract_bullets_from_markdown(markdown: str) -> str:
    """Returns a string containing only the bullet points from a markdown"""
    # Split the text into paragraphs
    paragraphs = re.split("\n\s*\n", markdown)

    # Initialize an empty list to store the list items
    list_items = []

    # Iterate over each paragraph
    for paragraph in paragraphs:
        # Split the paragraph into lines
        lines = paragraph.split("\n")
        # If the first line of the paragraph starts with a list marker,
        # add the entire paragraph to the list items
        if re.match("^\s*(\d+\.\s+|\-\s+|\*\s+|\+\s+).*", lines[0]):
            list_items.append(paragraph)

    # Join the list items with double newlines
    bullet_points_as_string = "\n\n".join(list_items)
    # Normalize the list items
    bullet_points_as_string = _normalize_markdown_list(bullet_points_as_string)
    return bullet_points_as_string


def save_markdown(file_name: str, markdown_content: str) -> None:
    """Save the markdown content as a file in the output directory"""
    path = get_root_directory() / "output" / file_name
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdown file {file_name} created successfully.")
