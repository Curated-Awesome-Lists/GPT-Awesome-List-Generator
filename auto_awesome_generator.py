import os
from typing import Tuple

from dotenv import load_dotenv

from connections.chatgpt import ChatApp
from data_pipelines import github, google_scholar, podcast, youtube
from utils import extract_bullets_from_markdown, save_markdown, timing


def get_prompt_per_data_type(
    keywords: str, description: str, data_type: str, sort_metric: str
) -> list[dict]:
    prompt = f"""
    I will provide a list of elements categorized as '{data_type}', each associated with a specific keyword '{keywords}' and an accompanying description "{description}". These elements are sorted based on '{sort_metric}'.
    
    Please perform the following tasks:
    1. Review the '{data_type}' and retain only those that are directly relevant to the given keyword and its respective description. 
    2. Format the filtered '{data_type}' into a visually appealing markdown unordered list. 
    3. Enhance the list's aesthetics and clarity for import into a markdown editor by adding an appropriate emoji next to each element, next to its '{sort_metric}' value.
    4. Ensure that the description of each item on the list is concise and coherent ideally 2-3 sentences long.
"
    """
    return [
        {"role": "user", "content": prompt},
        {
            "role": "assistant",
            "content": f"Ok. Provide me with the unfiltered '{data_type}'.",
        },
    ]


@timing
def generate_markdown_per_data_type(
    data_types_info: dict[str, dict[str, any]],
    chatgpt_client: ChatApp,
    model: str = "gpt-3.5-turbo",
    batch_size: int = 10,
) -> Tuple[dict[str, str], float]:
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
        if not extracted_data:
            print(f"No data found for '{key}'.")
            continue
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

    return markdown_contents, total_tokens


def merge_markdown_contents(markdown_contents: dict[str, str]) -> str:
    """Merge the markdown contents into one markdown"""
    markdown = ""
    for key, value in markdown_contents.items():
        markdown += f"## {key}\n\n"
        markdown += value + "\n"
    return markdown


def generate_awesome_list_markdown(
    data_markdown: str, keyword: str, description: str
) -> Tuple[str, float]:
    """Generate the final awesome list markdown"""
    chatgpt_client = ChatApp(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)) + "/connections",
            "chatgpt_setup_data",
            "awesome_list_context.json",
        ),
        api_key=os.environ["OPENAI_API_KEY"],
    )
    first_prompt = """
    I will give you a keyword, its description, and markdown code for various data sections 
    like GitHub projects or YouTube videos. Your task is to create an awesome list using 
    the given data, following these guidelines:
    1. Design an attractive awesome list with a table of contents and an official resources section at the top.
    2. Filter the official resources from the data using the keyword and description I provided.
    3. DO NOT add any new data to any data section; only use the given data to create the awesome list. 
    4. If a data section is empty delete it and don't add it to the awesome list
    Do you understand?
    """
    second_prompt = f"""Keyword is: {keyword}\nDescription is: {description}\nData in Markdown code is: {data_markdown}"""
    messages = [
        {"role": "user", "content": first_prompt},
        {
            "role": "assistant",
            "content": f"Ok I understand. Provide me with the keyword, description and "
            f"data in markdown format.",
        },
        {"role": "user", "content": second_prompt},
    ]
    chatgpt_client.messages.extend(messages)
    completion = chatgpt_client.send_messages()
    response_message = completion["choices"][0]["message"].content
    total_tokens = completion.usage.total_tokens
    return response_message, total_tokens


def save_and_return_awesome_list(
    keyword: str,
    description: str,
    model: str = "gpt-3.5-turbo-16k-0613",
    num_results=20,
) -> Tuple[str, dict]:
    """
    Performs a search for specified keywords across multiple data types, like GitHub
    projects, YouTube videos, Google Scholar papers, and podcasts. Then fetches the
    relevant data and utilizes ChatGPT to filter and craft a markdown section for each
    data type. Finally, it combines them to generate a comprehensive 'Awesome List'
    in Markdown format
    """
    load_dotenv()
    data_types = [
        ("GitHub projects", "the number of stars", github.get_github_search_results),
        ("YouTube videos", "the number of views", youtube.search_youtube),
        (
            "Google Scholar papers",
            "number of citations else relevance",
            google_scholar.scrape_google_scholar,
        ),
        ("podcasts", "their relevance", podcast.get_podcasts),
    ]
    data_types_info = {
        dt[0]: {
            "prompt": get_prompt_per_data_type(keyword, description, dt[0], dt[1]),
            "data": dt[2](keyword, num_results),
        }
        for dt in data_types
    }

    chatgpt_client = ChatApp(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "connections",
            "chatgpt_setup_data",
            "awesome_list_context.json",
        ),
        api_key=os.environ["OPENAI_API_KEY"],
    )

    markdown_contents, markdown_per_data_tokens = generate_markdown_per_data_type(
        data_types_info, chatgpt_client, model
    )
    merged_markdown = merge_markdown_contents(markdown_contents)
    awesome_list_markdown, awesome_list_tokens = generate_awesome_list_markdown(
        merged_markdown, keyword, description
    )
    usage_info = {"total_tokens": awesome_list_tokens + markdown_per_data_tokens}
    save_markdown(f"{keyword}.md", awesome_list_markdown)
    return awesome_list_markdown, usage_info


if __name__ == "__main__":
    k = "Auto-GPT"
    d = """Auto-GPT is an experimental open-source application showcasing the capabilities of the GPT-4 language model. This program, driven by GPT-4, chains together LLM "thoughts", to autonomously achieve whatever goal you set. As one of the first examples of GPT-4 running fully autonomously, Auto-GPT pushes the boundaries of what is possible with AI.
    """
    _, _ = save_and_return_awesome_list(k, d, "gpt-3.5-turbo-16k")
