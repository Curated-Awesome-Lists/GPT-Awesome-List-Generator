import json
import os
import re
from typing import Optional, Tuple

from dotenv import load_dotenv

from connections.chatgpt import ChatApp
from data_pipelines import github, google_scholar, podcast, youtube
from utils import extract_bullets_from_markdown, save_markdown, timing


def create_awesome_markdown_section(
    section_title: str, items: list[dict[str, str]]
) -> str:
    """Create a markdown section for the list of items
    each item in 'items' should follow the following format:
    {
        "title": "title",
        "link": "link",
        "description": "description",
        "sorting_metric": "sorting_metric: e.g. stars, views, etc." ,
        "sorting_metric_value": "sorting_metric_value: e.g. 100, 1000, etc."
    }
    """
    if not items or not isinstance(items, list):
        return ""
    # sort items based on the sorting metric
    try:
        sorted_items = sorted(
            items, key=lambda x: x.get("sorting_metric_value"), reverse=True
        )
    except Exception as e:
        print(f"Failed to sort the items: {e}")
        sorted_items = items
    # create the markdown section
    markdown_section = f"## {section_title}\n"
    for item in sorted_items:
        title = item.get("title", "")
        link = item.get("link", "")
        description = item.get("description", "")
        sorting_metric = item.get("sorting_metric", "")
        sorting_metric_value = item.get("sorting_metric_value", "")
        markdown_section += f"- [{title}]({link}): {description}\n"
        # add the sorting metric value between brackets with an emoji
        if sorting_metric == "stars":
            markdown_section += f"  - :star: {sorting_metric}: {sorting_metric_value}\n"
        elif sorting_metric == "views":
            markdown_section += f"  - :eyes: {sorting_metric}: {sorting_metric_value}\n"
        else:
            markdown_section += f"  - {sorting_metric}: {sorting_metric_value}\n"

    return markdown_section


functions = [
    {
        "name": "create_awesome_markdown_section",
        "description": "Create a markdown section for the list of items",
        "parameters": {
            "type": "object",
            "properties": {
                "section_title": {
                    "type": "string",
                    "description": "The title of the section",
                },
                "items": {
                    "type": "string",
                    "description": """JSON string of a list of items to be included in the section, item is a dictionary as follow: { "title": "title", "link": "link", "description": "description", "sorting_metric": "sorting_metric: e.g. stars, views, etc." , "sorting_metric_value": "sorting_metric_value: e.g. 100, 1000, etc." } """,
                },
            },
            "required": ["section_title", "items"],
        },
    }
]


def get_prompt(
    keywords: str, description: str, data_type: str, sort_metric: str
) -> list[dict]:
    prompt = f"""
    I am going to provide you with a list of '{data_type}' related to the keyword '{keywords}' and its description "{description}". 
    These '{data_type}' are sorted by '{sort_metric}'.

    I want you to:

    1. Filter the '{data_type}', retaining only those that are relevant to the keyword and its associated description. 
    2. return the filtered '{data_type}' as an interesting markdown Unordered list.  
    """
    return [
        {"role": "user", "content": prompt},
        {
            "role": "assistant",
            "content": f"Ok. Provide me with the unfiltered '{data_type}'.",
        },
    ]


def extract_json_array(s: str) -> Optional[list[any]]:
    match = re.search(r"\[.*\]", s, re.DOTALL)
    if not match:
        print("No JSON array found in the input string.")
        return None

    array_str = match.group()
    try:
        return json.loads(array_str)
    except json.JSONDecodeError as e:
        print(f"Could not decode JSON array: {e}")
        return None


@timing
def generate_markdown_per_data_type(
    data_types_info: dict[str, dict[str, any]],
    chatgpt_client: ChatApp,
    model: str = "gpt-3.5-turbo",
    batch_size: int = 10,
) -> Tuple[dict[str, str], dict[str, int]]:
    """Generate a markdown for each data type separately.

    Args:
        data_types_info: A dictionary containing information about each data type.
            The keys represent the data type, and the values are dictionaries with
            "prompt" and "data" keys. The "prompt" value is a list of strings
            representing prompt messages. The "data" value is a list of data to
            process.
        chatgpt_client: An instance of the ChatApp class for interacting with the
            ChatGPT API.
        model: The model to use for generating markdown. Defaults to "gpt-3.5-turbo".
        batch_size: The number of data items to process in each batch. Defaults to 10.

    Returns:
        A tuple containing two dictionaries. The first dictionary maps each data type
        to its corresponding generated markdown. The second dictionary contains the
        usage information, with the "total_tokens" key representing the total number
        of tokens used during generation.
    """
    markdown_contents = {}
    initial_chatgpt_client_messages = chatgpt_client.messages.copy()
    total_tokens = 0

    for key, value in data_types_info.items():
        prompt_messages = value["prompt"]
        extracted_data = value["data"]
        bullet_points = ""

        for i in range(0, len(extracted_data), batch_size):
            batch_data = extracted_data[i : i + batch_size]
            data_message = {
                "role": "user",
                "content": f"Ok, I will provide the data, please send the response ONLY as a markdown Unordered list. data for '{key}' is: {batch_data}",
            }

            # reset chatgpt client messages
            chatgpt_client.messages = initial_chatgpt_client_messages.copy()

            chatgpt_client.messages.extend(prompt_messages)
            chatgpt_client.messages.append(data_message)
            completion = chatgpt_client.send_messages(model=model)
            total_tokens += completion.usage.total_tokens

            response_message = completion["choices"][0]["message"].content
            batch_bullet_points = extract_bullets_from_markdown(response_message)
            bullet_points = bullet_points + batch_bullet_points + "\n"

        markdown_contents[key] = bullet_points

    usage_info = {"total_tokens": total_tokens}

    return markdown_contents, usage_info


def merge_markdown_contents(markdown_contents: dict[str, str]) -> str:
    """Merge the markdown contents into one markdown"""
    markdown = ""
    for key, value in markdown_contents.items():
        markdown += f"## {key}\n\n"
        markdown += value + "\n"
    return markdown


def generate_awesome_list(
    keywords: str, description: str, model: str = "gpt-3.5-turbo-16k-0613"
):
    github_prompt = get_prompt(
        keywords, description, "GitHub projects", "the number of stars"
    )
    youtube_prompt = get_prompt(
        keywords, description, "YouTube videos", "the number of views"
    )
    google_scholar_prompt = get_prompt(
        keywords,
        description,
        "Google Scholar papers",
        "number of citations else relevance",
    )
    podcast_prompt = get_prompt(keywords, description, "podcasts", "their relevance")

    load_dotenv()
    chatgpt_client = ChatApp(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)) + "/connections",
            "chatgpt_setup_data",
            "awesome_list_context.json",
        ),
        api_key=os.environ["OPENAI_API_KEY"],
    )
    number_of_results = 40
    data_types_info = {
        "Github Projects": {
            "prompt": github_prompt,
            "data": github.get_github_search_results(keywords, number_of_results),
        },
        "Youtube Videos": {
            "prompt": youtube_prompt,
            "data": youtube.search_youtube(keywords, number_of_results),
        },
        "Google Scholars": {
            "prompt": google_scholar_prompt,
            "data": google_scholar.scrape_google_scholar(keywords, number_of_results),
        },
        "Podcasts": {
            "prompt": podcast_prompt,
            "data": podcast.get_podcasts(keywords, number_of_results),
        },
    }
    markdown_contents, _ = generate_markdown_per_data_type(
        data_types_info, chatgpt_client, model
    )
    merged_markdown = merge_markdown_contents(markdown_contents)
    save_markdown(f"{k}.md", merged_markdown)


if __name__ == "__main__":
    k = "Auto-GPT"
    d = """Auto-GPT is an experimental open-source application showcasing the capabilities of the GPT-4 language model. This program, driven by GPT-4, chains together LLM "thoughts", to autonomously achieve whatever goal you set. As one of the first examples of GPT-4 running fully autonomously, Auto-GPT pushes the boundaries of what is possible with AI.
    """
    generate_awesome_list(k, d, "gpt-3.5-turbo-16k")
