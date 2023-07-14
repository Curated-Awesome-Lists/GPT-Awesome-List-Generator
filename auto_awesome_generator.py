import json
import os
from typing import Dict
import re
import json
from dotenv import load_dotenv

from connections.chatgpt import ChatApp
from data_pipelines import github, google_scholar, podcast, youtube
from utils import get_root_directory, extract_bullets


def create_awesome_markdown_section(section_title: str, items: list[Dict[str, str]]):
    """Create a markdown section for the list of items
    item is a dictionary as follow:
    {
        "title": "title",
        "link": "link",
        "description": "description",
        "sorting_metric": "sorting_metric: e.g. stars, views, etc." ,
        "sorting_metric_value": "sorting_metric_value: e.g. 100, 1000, etc."
    }
    """
    # make sure items not None or not array
    if not items or not isinstance(items, list):
        return ""
    # Convert items from JSON to Python
    # items = json.loads(items)
    # sort the items based on the sorting metric
    try:
        sorted_items = sorted(items, key=lambda x: x.get("sorting_metric_value"), reverse=True)
    except Exception as e:
        print(f"Failed to sort the items: {e}")
        sorted_items = items
    # create the markdown section
    markdown_section = f"## {section_title}\n"
    for item in items:
        title = item.get('title', '')
        link = item.get('link', '')
        description = item.get('description', '')
        sorting_metric = item.get('sorting_metric', '')
        sorting_metric_value = item.get('sorting_metric_value', '')
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


def save_awesome_list(file_name: str, markdown_content: str) -> None:
    """Save the markdown content as a file in the output directory"""
    path = get_root_directory() / "output" / file_name
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdown file {file_name} created successfully.")


def get_prompt(data_type: str, sort_metric: str, keywords: str, description: str):
    prompt = f"""
    I am going to provide you with a list of '{data_type}' related to the keyword '{keywords}' and its description "{description}". 
    These '{data_type}' are sorted by '{sort_metric}'.

    I want you to:

    1. Filter the '{data_type}', retaining only those that are relevant to the keyword and its associated description. 
    2. return the filtered '{data_type}' as an interesting markdown Unordered list.  
    """
    return [
        {
            "role": "user",
            "content": prompt
        },
        {
            "role": "assistant",
            "content": f"Ok. Provide me with the unfiltered '{data_type}'."
        }
    ]


def extract_json_array(s):
    match = re.search(r'\[.*\]', s, re.DOTALL)
    if match:
        array_str = match.group()
        try:
            return json.loads(array_str)
        except json.JSONDecodeError:
            print("Could not decode JSON array.")
            return None
    else:
        print("No JSON array found in the input string.")
        return None


def generate_markdown_per_data_type(data_types_info: dict, chatgpt_client: ChatApp, model: str = "gpt-3.5-turbo",
                                    batch_size: int = 10) -> Dict[str, str]:
    """Generate a markdown for each data type separately"""
    markdown_contents = {}
    for key, value in data_types_info.items():
        prompt_messages = value["prompt"]
        extracted_data = value["data"]
        bullet_points = ''
        # Process data in batches
        for i in range(0, len(extracted_data), batch_size):
            batch_data = extracted_data[i:i + batch_size]
            data_message = {"role": "user",
                            "content": f"Ok, I will provide the data, please send the response ONLY as a markdown Unordered list. data for '{key}' is: {batch_data}"}
            chatgpt_client.messages.extend(prompt_messages)
            chatgpt_client.messages.append(data_message)
            completion = chatgpt_client.send_messages(model=model)
            completion = completion["choices"][0]["message"].content
            batch_bullet_points = extract_bullets(completion)
            bullet_points += batch_bullet_points + '\n'
        markdown_contents[key] = bullet_points
    return markdown_contents


def merge_markdown_contents(markdown_contents: Dict[str, str]) -> str:
    """Merge the markdown contents into one markdown"""
    markdown = ""
    for key, value in markdown_contents.items():
        markdown += f"## {key}\n\n"
        markdown += value + "\n"
    return markdown


def generate_awesome_list(keywords: str, description: str, model: str = "gpt-3.5-turbo-16k-0613"):
    github_prompt = get_prompt("GitHub projects", "the number of stars", keywords, description)
    youtube_prompt = get_prompt("YouTube videos", "the number of views", keywords, description)
    google_scholar_prompt = get_prompt("Google Scholar papers", "number of citations else relevance", keywords,
                                       description)
    podcast_prompt = get_prompt("podcasts", "their relevance", keywords, description)

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
            "data": github.get_github_search_results(keywords, number_of_results)
        },
        "Youtube Videos": {
            "prompt": youtube_prompt,
            "data": youtube.search_youtube(keywords, number_of_results)
        },
        "Google Scholars": {
            "prompt": google_scholar_prompt,
            "data": google_scholar.scrape_google_scholar(keywords, number_of_results)
        },
        "Podcasts": {
            "prompt": podcast_prompt,
            "data": podcast.get_podcasts(keywords, number_of_results)
        }
    }
    markdown_contents = generate_markdown_per_data_type(data_types_info, chatgpt_client, model)
    merged_markdown = merge_markdown_contents(markdown_contents)
    save_awesome_list(f"{k}.md", merged_markdown)


if __name__ == "__main__":
    k = "Auto-GPT"
    d = """Auto-GPT is an experimental open-source application showcasing the capabilities of the GPT-4 language model. This program, driven by GPT-4, chains together LLM "thoughts", to autonomously achieve whatever goal you set. As one of the first examples of GPT-4 running fully autonomously, Auto-GPT pushes the boundaries of what is possible with AI.
    """
    generate_awesome_list(k, d, 'gpt-3.5-turbo-16k')
