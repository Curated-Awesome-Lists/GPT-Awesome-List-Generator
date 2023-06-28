import json
import os
import openai
from dotenv import load_dotenv

from utils import get_project_root

load_dotenv()


class ChatApp:
    def __init__(self, setup_file_path):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        with open(setup_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = data

    # "gpt-3.5-turbo" or "gpt-4"
    def send_messages(self, model="gpt-3.5-turbo", tries=1):
        response = openai.ChatCompletion.create(
            model=model,
            messages=self.messages,
            n=tries,  # how many chat completion choices
        )
        return response["choices"][0]["message"].content


if __name__ == "__main__":
    chatgpt_client = ChatApp(
        get_project_root()
        / "connections"
        / "chatgpt_setup_data"
        / "awesome_list_context.json",
    )
    print(chatgpt_client.send_messages())
