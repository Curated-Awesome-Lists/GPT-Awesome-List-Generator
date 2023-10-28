from section_data_pipelines import github, google

from enum import Enum


class GithubMode(Enum):
    REPO = "repo"
    TOPIC = "topic"
    COLLECTION = "collection"


class SectionDataExtractor:
    def __init__(self, keyword: str, description: str, num_results: int = 20,
                 github_mode: GithubMode = GithubMode.REPO):
        self.keyword = keyword
        self.description = description
        self.num_results = num_results

        github_function = github.get_github_search_results
        if github_mode == GithubMode.TOPIC:
            github_function = github.get_github_topic_results
        elif github_mode == GithubMode.COLLECTION:
            github_function = github.get_github_collection_results

        self.data_pipelines = [
            ("GitHub projects", "the number of stars", github_function),
            ("Articles & Blogs", "their relevance", google.search_google_for_articles),
            ("Online Courses", "their relevance", google.search_google_for_courses),
            ("Books", "their relevance", google.search_google_for_books),
            ("Research Papers", "their relevance", google.search_google_for_research),
            ("Videos", "their relevance", google.search_google_for_videos),
            ("Tools & Software", "their relevance", google.search_google_for_tools_software),
            ("Conferences & Events", "their relevance",
             google.search_google_for_conferences_or_events),
            ("Slides & Presentations", "their relevance", google.search_google_for_slides_or_presentations),
            ("Podcasts", "their relevance", google.search_google_for_podcasts),
        ]

    def get_data(self) -> dict:
        return {
            dt[0]: {
                "prompt": self._get_prompt_per_pipeline(dt[0], dt[1]),
                "data": dt[2](self.keyword, self.num_results),
            }
            for dt in self.data_pipelines
        }

    def _get_prompt_per_pipeline(self, data_type: str, sort_metric: str) -> list[dict]:
        prompt = f"""
        I will provide a list of items categorized as '{data_type}'. They are supposed to be related to "{self.keyword}, {self.description}". These items are sorted based on '{sort_metric}'.

        I want you to do the following
        1. Review the items and filter out any unrelated items to the given description. 
        2. Format the items into a markdown unordered list and add appropriate emoji if makes sense. 
        4. Ensure that the description of each item on the list is concise ideally 2-3 sentences long.
        "
        """
        return [
            {"role": "user", "content": prompt},
            {
                "role": "assistant",
                "content": f"Ok. Provide me with the unfiltered '{data_type}'.",
            },
        ]
