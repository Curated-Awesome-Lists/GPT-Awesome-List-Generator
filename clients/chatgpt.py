import json
import re
import openai
from openai import OpenAI
from dotenv import load_dotenv
from utils import get_root_directory
import os
import time


def get_sleep_seconds_for_openai_api(error_msg):
    """Extract sleep duration from the error message sent by the OpenAI API"""
    match = re.search(r"Please try again in (\d+)s", error_msg)
    if match:
        return int(match.group(1))
    else:
        return 60  # Default sleep duration in case regex fails


class ChatApp:
    def __init__(self, setup_file_path, api_key: str):
        self.client = OpenAI(api_key=api_key)
        with open(setup_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = data

    def send_messages(self, model="o1-mini-2024-09-12", tries=1):
        if model.startswith("o1"):
            self.messages[0]["role"] = "user"
        while True:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=self.messages,
                    n=tries,
                )
                return response
            except openai.APIError as e:
                sleep_duration = get_sleep_seconds_for_openai_api(str(e))
                print(f"Rate limit reached. Sleeping for {sleep_duration} seconds...")
                time.sleep(sleep_duration)


if __name__ == "__main__":
    load_dotenv()
    chatgpt_client = ChatApp(
        os.path.join(
            get_root_directory(),
            "clients",
            "setup_data",
            "awesome_list_context.json",
        ),
        api_key=os.environ["OPENAI_API_KEY"],
    )
    print(chatgpt_client.send_messages())
