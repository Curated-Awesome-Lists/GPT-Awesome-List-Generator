import os
from typing import Tuple, Union

from joblib import delayed, Parallel

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

    def process_one_data_type(
        self, data_type_key: str, data_type_info: dict, batch_size: int
    ) -> Tuple[str, Union[str, None], int]:
        """
        Process a specific type of data and returns the data type key, bullet points,
        and total tokens used.

        Args:
            data_type_key (str): The key that identifies the type of data to process.
            data_type_info (dict): Dictionary contains the prompts and extracted data
            batch_size (int): The size of each batch of data to process at a time.

        Returns:
            tuple: Returns a tuple of three items:
                - The data type key (str)
                - The bullet points extracted from the responses (str), or None if no
                data was found for the given key
                - The total number of tokens used in the processing (int)
        """
        initial_client_messages = self.client.messages.copy()
        total_tokens = 0
        bullet_points = ""

        prompt_messages = data_type_info["prompt"]
        extracted_data = data_type_info["data"]
        if not extracted_data:
            print(f"No data found for '{data_type_key}'.")
            return data_type_key, None, 0

        data_type_client_messages = initial_client_messages + prompt_messages
        for i in range(0, len(extracted_data), batch_size):
            batch_data = extracted_data[i : i + batch_size]
            data_message = {
                "role": "user",
                "content": f"Ok, I will provide the data, please send the response ONLY as a markdown Unordered list. "
                f"data for '{data_type_key}' is: {batch_data}",
            }
            self.client.messages = data_type_client_messages.copy()
            self.client.messages.append(data_message)
            completion = self.client.send_messages(model=self.model)
            total_tokens += completion.usage.total_tokens

            response_message = completion.choices[0].message.content
            batch_bullet_points = extract_bullets_from_markdown(response_message)
            bullet_points = bullet_points + batch_bullet_points + "\n"

        return data_type_key, bullet_points, total_tokens

    @timing
    def generate_markdown(
        self, data_types_info: dict, batch_size: int
    ) -> Tuple[dict[str, str], float]:
        markdown_contents = {}
        total_tokens = 0

        results = Parallel(n_jobs=-1, backend="threading")(
            delayed(self.process_one_data_type)(key, value, batch_size)
            for key, value in data_types_info.items()
        )

        for key, bullet_points, tokens in results:
            if bullet_points is not None:
                markdown_contents[key] = bullet_points
                total_tokens += tokens

        return markdown_contents, total_tokens
