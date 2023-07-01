from connections import github, google_scholar, podcast, youtube
from connections.chatgpt import ChatApp
import os
import re

from utils import get_project_root

# Set these two keys to create a new awesome list
keyword = "Data Version Control (DVC)"
description = """Data Version Control is a free, open-source tool for data management, 
ML pipeline automation, and experiment management. This helps data science and machine 
learning teams manage large datasets, make projects reproducible, and collaborate better
"""


def get_awesome_list_input_data() -> dict:
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


def append_data_to_chatgpt_client_messages(chatgp_client: ChatApp) -> None:
    """Append the data from get_awesome_list_input_data() chatgpt_client.messages"""
    data = get_awesome_list_input_data()
    for k, v in data.items():
        chatgp_client.messages.append({"role": "user", "content": f"{k}: {v}"})


def extract_markdown_from_str(text: str) -> str:
    lines = text.split("\n")
    markdown_lines = [
        line for line in lines if re.match(r"^(\s*[-*]|\s*#+\s*|\[.*\]\(.*\))", line)
    ]
    return "\n".join(markdown_lines)


def create_awesome_markdown() -> None:
    """Create a markdown file as keyword.md created by chatgpt"""
    chatgpt_client = ChatApp(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)) + "/connections",
            "chatgpt_setup_data",
            "awesome_list_context.json",
        )
    )
    append_data_to_chatgpt_client_messages(chatgpt_client)
    response = chatgpt_client.send_messages()

    markdown_content = extract_markdown_from_str(response)
    file_name = f"{keyword}.md"
    path = get_project_root() / "output" / file_name
    with open(path, "w") as f:
        f.write(markdown_content)

    print(f"Markdown file {file_name} created successfully.")


if __name__ == "__main__":
    # Set the global variables keyword and description to create a new awesome list.
    create_awesome_markdown()
