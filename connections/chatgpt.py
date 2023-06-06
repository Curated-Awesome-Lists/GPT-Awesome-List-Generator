import os
import openai
import json


class ChatApp:
    def __init__(self, setup_file_path):
        openai.organization = os.getenv("OPENAI_ORG")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        with open(setup_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = data

    # "gpt-3.5-turbo" or "gpt-4"
    def chat(self, prompt, model="gpt-3.5-turbo", tries=1):
        self.messages.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model=model,
            messages=self.messages,
            n=tries,  # how many chat completion choices
        )
        return response["choices"][0]["message"].content


if __name__ == "__main__":
    os.environ["OPENAI_ORG"] = ""
    os.environ["OPENAI_API_KEY"] = ""
    chatgpt_clien = ChatApp(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "chatgpt_setup_data",
            "awesome_list_context.json",
        )
    )
    print(chatgpt_clien.chat("The idea is AutoGPT and the data: "))
