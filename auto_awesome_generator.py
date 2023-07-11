import os
from typing import Dict, Tuple

from dotenv import load_dotenv

from connections.chatgpt import ChatApp
from data_pipelines import github, google_scholar, podcast, youtube
from utils import extract_markdown_from_str, get_root_directory, timing


@timing
def get_awesome_list_input_data(keyword: str, description: str) -> dict:
    return_data = {
        "Keyword and Description": f"keyword: {keyword}, description: {description}"
    }
    github_projects = github.get_github_search_results(keyword)
    return_data["Github Projects"] = github_projects
    google_scholars = google_scholar.scrape_google_scholar(keyword)
    return_data["Google Scholars"] = google_scholars
    youtube_videos = youtube.search_youtube(keyword)
    return_data["Youtube Videos"] = youtube_videos
    podcasts = podcast.get_podcasts(keyword)
    return_data["Podcasts"] = podcasts
    return return_data


def get_data_as_chatgpt_client_messages(data: dict) -> list[dict]:
    """Append the data from get_awesome_list_input_data() in a chatgpt_client.messages
    readable format."""
    messages = []
    for k, v in data.items():
        messages.append({"role": "user", "content": f"{k}: {v}"})
    return messages


@timing
def generate_and_return_awesome_list(
        chatgpt_client: ChatApp, model: str = "gpt-3.5-turbo"
) -> Tuple[str, Dict[str, int]]:
    """Generate an awesome list using the chatgpt_client and the data"""
    completion = chatgpt_client.send_messages(model=model)

    usage_info = {
        "tokens": completion.usage.total_tokens,
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
    }
    response = completion["choices"][0]["message"].content
    markdown_content = extract_markdown_from_str(response)
    return markdown_content, usage_info


def save_awesome_list(file_name: str, markdown_content: str) -> None:
    """Save the markdown content as a file in the output directory"""
    path = get_root_directory() / "output" / file_name
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdown file {file_name} created successfully.")


def get_prompt(data_type: str, sort_metric: str, keywords: str, description: str):
    prompt = f"""
    I am going to provide you with a list of {data_type} related to the keyword "{keywords}" and its description "{description}". These {data_type} are sorted by {sort_metric}.

    I want you to:

    1. Filter the {data_type}, retaining only those that are relevant to the keyword and its associated description. 
    2. Prioritize the filtered entries based on their relevance and {sort_metric}.
    3. Generate an 'Awesome List' section for these {data_type} in markdown format.
    4. Generate the list starting with section name to be the data type as a markdown header (e.g. ## {data_type}), then list the items in mardown style as points.
    5. Make sure to include the links to the {data_type} in the markdown and make it as interesting as possible with short description.

    Please disregard any {data_type} that do not seem relevant to the keyword and description.
    """
    return [
        {
            "role": "user",
            "content": prompt
        },
        {
            "role": "assistant",
            "content": f"Ok. Provide me with the unfiltered {data_type}."
        }
    ]


def generate_markdown_per_data_type(data_types_info: dict, chatgpt_client: ChatApp, model: str = "gpt-3.5-turbo") -> \
        Dict[
            str, str]:
    """Generate a markdown for each data type separately"""
    markdown_contents = {}
    for key, value in data_types_info.items():
        prompt_messages = value["prompt"]
        extracted_data = value["data"]
        data_message = {"role": "user", "content": f"Ok, data for {key} is: {extracted_data}"}
        chatgpt_client.messages = prompt_messages
        chatgpt_client.messages.append(data_message)
        completion = chatgpt_client.send_messages(model=model)
        response = completion["choices"][0]["message"].content
        markdown_contents[key] = extract_markdown_from_str(response)
    return markdown_contents


def merge_markdowns(markdown_contents: Dict[str, str]) -> str:
    """Merge markdowns into a single string"""
    merged_markdown = ""
    for key, value in markdown_contents.items():
        merged_markdown += f"## {key}\n\n{value}\n\n"
    return merged_markdown


def generate_awesome_list(keywords: str, description: str, model: str = "gpt-3.5-turbo"):
    github_prompt = get_prompt("GitHub projects", "the number of stars", keywords, description)
    youtube_prompt = get_prompt("YouTube videos", "the number of views", keywords, description)
    google_scholar_prompt = get_prompt("Google Scholar results", "their relevance", keywords, description)
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
    data_types_info = {
        "Github Projects": {
            "prompt": github_prompt,
            "data": github.get_github_search_results(keywords, 40)
        },
        "Youtube Videos": {
            "prompt": youtube_prompt,
            "data": youtube.search_youtube(keywords, 40)
        },
        "Google Scholars": {
            "prompt": google_scholar_prompt,
            "data": google_scholar.scrape_google_scholar(keywords)
        },
        "Podcasts": {
            "prompt": podcast_prompt,
            "data": podcast.get_podcasts(keywords, 40)
        }
    }
    markdown_contents = generate_markdown_per_data_type(data_types_info, chatgpt_client, model)
    merged_markdown = merge_markdowns(markdown_contents)
    save_awesome_list(f"{k}.md", merged_markdown)


if __name__ == "__main__":
    # Set these two keys to create a new awesome list
    k = "Auto-GPT"
    d = """Auto-GPT is an experimental open-source application showcasing the capabilities of the GPT-4 language model. This program, driven by GPT-4, chains together LLM "thoughts", to autonomously achieve whatever goal you set. As one of the first examples of GPT-4 running fully autonomously, Auto-GPT pushes the boundaries of what is possible with AI.
    """
    generate_awesome_list(k, d)
