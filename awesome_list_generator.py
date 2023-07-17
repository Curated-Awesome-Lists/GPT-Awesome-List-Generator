import os
from typing import Tuple

from dotenv import load_dotenv

from clients.chatgpt import ChatApp
from section_data_extractor import SectionDataExtractor
from section_markdown_generator import SectionMarkdownGenerator
from utils import save_markdown

load_dotenv()


class AwesomeListGenerator:

    def __init__(self, keyword: str, description: str, model: str = "gpt-3.5-turbo-16k",
                 data_extraction_batch_size: int = 10):
        self.keyword = keyword
        self.description = description
        self.model = model
        self.data_extraction_batch_size = data_extraction_batch_size

        self.client = ChatApp(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "clients",
                "setup_data",
                "awesome_list_context.json",
            ),
            api_key=os.environ["OPENAI_API_KEY"],
        )

        self.section_data_extractor = SectionDataExtractor(keyword=keyword, description=description, num_results=20)
        self.section_generator = SectionMarkdownGenerator()

    def save_and_return_awesome_list(self) -> Tuple[str, dict]:
        data_types_info = self.section_data_extractor.get_data()
        markdown_contents, markdown_per_data_tokens = self.section_generator.generate_markdown(
            data_types_info, self.model, batch_size=self.data_extraction_batch_size
        )
        merged_markdown = self._merge_markdown_contents(markdown_contents)
        awesome_list_markdown, awesome_list_tokens = self._generate_awesome_list_markdown(
            merged_markdown
        )
        usage_info = {"total_tokens": awesome_list_tokens + markdown_per_data_tokens}
        save_markdown(f"{self.keyword}.md", awesome_list_markdown)
        return awesome_list_markdown, usage_info

    @staticmethod
    def _merge_markdown_contents(markdown_contents: dict[str, str]) -> str:
        markdown = ""
        for key, value in markdown_contents.items():
            markdown += f"## {key}\n\n"
            markdown += value + "\n"
        return markdown

    def _generate_awesome_list_markdown(
            self, data_markdown: str
    ) -> Tuple[str, float]:
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
        second_prompt = f"""Keyword is: {self.keyword}\nDescription is: {self.description}\nData in Markdown code is: {data_markdown}"""
        messages = [
            {"role": "user", "content": first_prompt},
            {
                "role": "assistant",
                "content": f"Ok I understand. Provide me with the keyword, description and "
                           f"data in markdown format.",
            },
            {"role": "user", "content": second_prompt},
        ]
        self.client.messages.extend(messages)
        completion = self.client.send_messages()
        response_message = completion["choices"][0]["message"].content
        total_tokens = completion.usage.total_tokens
        return response_message, total_tokens
