from dotenv import load_dotenv

from section_data_extractor import SectionDataExtractor
from section_markdown_generator import SectionMarkdownGenerator
from utils import save_markdown

load_dotenv()


class AwesomeListGenerator:
    """
    A class used to generate a markdown awesome list for a specific keyword.

    ...

    Attributes
    ----------
    keyword : str
        the keyword for which the awesome list will be generated. This is needed to fetch the data from the data sources,
        for example, the GitHub API requires a keyword to search for repositories projects
        The keyword is also used to generate the title of the awesome list in the markdown file
    description : str
        a description related to the keyword
    model : str
        the OpenAI model to be used for generating the markdown (default is "gpt-3.5-turbo-16k")
    data_extraction_batch_size : int
        the number of data items to process in each batch (default is 20)
        For example, if the batch size is 10, then the data will be fetched from the data sources in batches of 10 (like 10 github projects at a time)
    number_of_results : int
        the number of results to fetch from each data source (default is 20). For example, fetch 20 github projects then process them with LLM model in batches based on data_extraction_batch_size.
    section_data_extractor : SectionDataExtractor
        an object of SectionDataExtractor to extract the data for each section
    section_generator : SectionMarkdownGenerator
        an object of SectionMarkdownGenerator to generate the markdown for each section from the extracted data

    Methods
    -------
    save_and_return_awesome_list():
        Generates and saves the awesome list into a markdown file, and returns the markdown content
    """

    def __init__(
        self,
        keyword: str,
        description: str,
        model: str = "gpt-3.5-turbo-16k",
        data_extraction_batch_size: int = 10,
        number_of_results: int = 20,
    ):
        """
        Constructs all the necessary attributes for the AwesomeListGenerator object.

        Parameters
        ----------
            keyword : str
                the keyword for which the awesome list will be generated
            description : str
                a description related to the keyword
            model : str
                the OpenAI model to be used for generating the markdown (default is "gpt-3.5-turbo-16k")
            data_extraction_batch_size : int
                the number of data items to process in each batch (default is 10)
            number_of_results : int
                the number of results to fetch from each data source (default is 40)
        """

        self.keyword = keyword
        self.description = description
        self.model = model
        self.data_extraction_batch_size = data_extraction_batch_size
        self.section_data_extractor = SectionDataExtractor(
            keyword=keyword, description=description, num_results=number_of_results
        )
        self.section_generator = SectionMarkdownGenerator(model)

    def save_and_return_awesome_list(self) -> tuple[str, dict[str, float]]:
        """
        Generates and saves the awesome list into a markdown file, and returns the markdown content.

        Returns
        -------
        str
            a string representing the content of the awesome list in markdown format
        """

        data_types_info = self.section_data_extractor.get_data()
        markdown_contents, total_tokens = self.section_generator.generate_markdown(
            data_types_info, batch_size=self.data_extraction_batch_size
        )
        merged_markdown = self._merge_markdown_contents(markdown_contents)
        save_markdown(f"{self.keyword}.md", merged_markdown)
        usage_info = {"total_tokens": total_tokens}
        return merged_markdown, usage_info

    def _merge_markdown_contents(self, markdown_contents: dict[str, str]) -> str:
        """
        Merges the markdown contents of all sections into one markdown, adds a main title, a description,
        and a table of contents.

        Parameters
        ----------
            markdown_contents : dict[str, str]
                a dictionary mapping each section to its corresponding markdown content

        Returns
        -------
        str
            a string representing the merged markdown content
        """

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
