import json

import openai

from utils import get_root_directory


class ChatApp:
    def __init__(self, setup_file_path, api_key: str):
        openai.api_key = api_key
        with open(setup_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = data

    # "gpt-3.5-turbo" or "gpt-4"
    def send_messages(self, model="gpt-3.5-turbo", tries=1):
        completion = openai.ChatCompletion.create(
            model=model,
            messages=self.messages,
            n=tries,  # how many chat completion choices
        )
        return completion


if __name__ == "__main__":
    chatgpt_client = ChatApp(
        get_root_directory()
        / "connections"
        / "chatgpt_setup_data"
        / "awesome_list_context.json",
    )
    print(chatgpt_client.send_messages())
