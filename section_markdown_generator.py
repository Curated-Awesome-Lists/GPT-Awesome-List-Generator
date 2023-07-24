import os
from typing import Tuple

from clients.chatgpt import ChatApp
from utils import extract_bullets_from_markdown, get_root_directory, timing


class SectionMarkdownGenerator:
    def __init__(self, model):
        self.model = model
        self.client = ChatApp(
            os.path.join(
                get_root_directory(),
                "clients",
                "setup_data",
                "awesome_list_context.json",
            ),
            api_key=os.environ["OPENAI_API_KEY"],
        )

    @timing
    def generate_markdown(
        self, data_types_info: dict, batch_size: int
    ) -> Tuple[dict[str, str], float]:
        markdown_contents = {}
        total_tokens = 0

        initial_client_messages = self.client.messages.copy()
        for key, value in data_types_info.items():
            prompt_messages = value["prompt"]
            extracted_data = value["data"]
            if not extracted_data:
                print(f"No data found for '{key}'.")
                continue

            bullet_points = ""
            client_data_type_messages = initial_client_messages + prompt_messages
            for i in range(0, len(extracted_data), batch_size):
                batch_data = extracted_data[i : i + batch_size]
                data_message = {
                    "role": "user",
                    "content": f"Ok, I will provide the data, please send the response ONLY as a markdown Unordered list. data for '{key}' is: {batch_data}",
                }
                self.client.messages = client_data_type_messages.copy()
                self.client.messages.append(data_message)
                completion = self.client.send_messages(model=self.model)
                total_tokens += completion.usage.total_tokens

                response_message = completion["choices"][0]["message"].content
                batch_bullet_points = extract_bullets_from_markdown(response_message)
                bullet_points = bullet_points + batch_bullet_points + "\n"

            markdown_contents[key] = bullet_points
            self.client.messages = initial_client_messages

        return markdown_contents, total_tokens
