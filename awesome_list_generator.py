from dotenv import load_dotenv
from section_data_extractor import SectionDataExtractor
from section_markdown_generator import SectionMarkdownGenerator
from utils import save_markdown

load_dotenv()


class AwesomeListGenerator:

    def __init__(
            self,
            keyword: str,
            description: str,
            model: str = "gpt-3.5-turbo-16k",
            data_extraction_batch_size: int = 10,
            number_of_results: int = 40):
        self.keyword = keyword
        self.description = description
        self.model = model
        self.data_extraction_batch_size = data_extraction_batch_size
        self.section_data_extractor = SectionDataExtractor(keyword=keyword, description=description,
                                                           num_results=number_of_results)
        self.section_generator = SectionMarkdownGenerator(model)

    def save_and_return_awesome_list(self) -> str:
        data_types_info = self.section_data_extractor.get_data()
        markdown_contents, markdown_per_data_tokens = self.section_generator.generate_markdown(
            data_types_info, batch_size=self.data_extraction_batch_size
        )
        merged_markdown = self._merge_markdown_contents(markdown_contents)
        save_markdown(f"{self.keyword}.md", merged_markdown)
        return merged_markdown

    def _merge_markdown_contents(self, markdown_contents: dict[str, str]) -> str:
        markdown = f"# Awesome {self.keyword}\n\n"
        markdown += f"{self.description}\n\n"

        markdown += "## Table of Contents\n\n"

        for key in markdown_contents.keys():
            markdown += f"- [{key}](#{key.lower().replace(' ', '-')})\n"
        markdown += "\n"

        for key, value in markdown_contents.items():
            markdown += f"## {key}\n\n"
            markdown += value + "\n"

        return markdown
