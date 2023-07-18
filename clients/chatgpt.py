import json
import re
import openai
from dotenv import load_dotenv
from utils import get_root_directory
import os
import time


def get_sleep_seconds_for_openai_api(error_msg):
    """Extract sleep duration from the error message sent by the OpenAI API"""
    match = re.search("Please try again in (\d+)s", error_msg)
    if match:
        return int(match.group(1))
    else:
        return 60  # Default sleep duration in case regex fails for some reason


class ChatApp:
    def __init__(self, setup_file_path, api_key: str):
        openai.api_key = api_key
        with open(setup_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = data

    # "gpt-4-32k", or "gpt-4-0613"
    def send_messages(self, model="gpt-3.5-turbo-16k-0613", tries=1):
        while True:
            try:
                completion = openai.ChatCompletion.create(
                    model=model,
                    messages=self.messages,
                    n=tries,  # how many chat completion choices
                )
                return completion
            except openai.error.RateLimitError as e:
                sleep_duration = get_sleep_seconds_for_openai_api(str(e))
                print(f"Rate limit reached. Sleeping for {sleep_duration} seconds...")
                time.sleep(sleep_duration)


if __name__ == "__main__":
    load_dotenv()
    chatgpt_client = ChatApp(
        get_root_directory()
        / "connections"
        / "setup_data"
        / "awesome_list_context.json",
        api_key=os.environ["OPENAI_API_KEY"],
    )
    print(chatgpt_client.send_messages())
