import os
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
    return bullet_points_as_string


if __name__ == "__main__":
    import re

    markdown_text = """Here is the filtered list of relevant GitHub projects related to the keyword "Auto-GPT" and its description:

    1. [Auto-GPT](https://github.com/Significant-Gravitas/Auto-GPT): An experimental open-source attempt to make GPT-4 fully autonomous.
    Additional details for Auto-GPT. (143754 stars)
    dasdasdasd
    - [Auto-GPT-Plugins](https://github.com/Significant-Gravitas/Auto-GPT-Plugins): Plugins for Auto-GPT. (3368 stars)
    * [Auto-GPT中文版本及爱好者组织](https://github.com/kaqijiang/Auto-GPT-ZH): Auto-GPT Chinese version and enthusiast organization. (2194 stars)
    + [Free-Auto-GPT](https://github.com/IntelligenzaArtificiale/Free-Auto-GPT): Free Auto GPT with NO paid API is a repository that offers a simple version of Auto GPT, an autonomous AI agent capable of performing tasks independently. (1955 stars)

    Please note that the list is sorted by the number of stars each project has received."""

    bullet_points_as_string = extract_bullets_from_markdown(markdown_text)

    print(bullet_points_as_string)


def save_markdown(file_name: str, markdown_content: str) -> None:
    """Save the markdown content as a file in the output directory"""
    path = get_root_directory() / "output" / file_name
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdown file {file_name} created successfully.")
