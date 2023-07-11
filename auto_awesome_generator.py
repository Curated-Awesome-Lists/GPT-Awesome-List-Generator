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
    with open(path, "w") as f:
        f.write(markdown_content)

    print(f"Markdown file {file_name} created successfully.")


if __name__ == "__main__":
    # Set these two keys to create a new awesome list
    k = "Data Version Control (DVC)"
    d = """Data Version Control is a free, open-source tool for data management, 
    ML pipeline automation, and experiment management. This helps data science and machine 
    learning teams manage large datasets, make projects reproducible, and collaborate better
    """
    load_dotenv()
    chatgpt_client = ChatApp(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)) + "/connections",
            "chatgpt_setup_data",
            "awesome_list_context.json",
        ),
        api_key=os.environ["OPENAI_API_KEY"],
    )
    data = get_awesome_list_input_data(k, d)
    data_messages = get_data_as_chatgpt_client_messages(data)
    chatgpt_client.messages.extend(data_messages)
    response, _ = generate_and_return_awesome_list(chatgpt_client)
    save_awesome_list(f"{k}.md", response)
