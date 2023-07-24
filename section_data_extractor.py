from section_data_pipelines import google_scholar, github, youtube, podcast


class SectionDataExtractor:
    def __init__(self, keyword: str, description: str, num_results: int = 20):
        self.keyword = keyword
        self.description = description
        self.num_results = num_results

        self.data_pipelines = [
            (
                "GitHub projects",
                "the number of stars",
                github.get_github_search_results,
            ),
            ("YouTube videos", "the number of views", youtube.search_youtube),
            (
                "Google Scholar papers",
                "number of citations else relevance",
                google_scholar.scrape_google_scholar,
            ),
            ("podcasts", "their relevance", podcast.get_podcasts),
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
        I will provide a list of elements categorized as '{data_type}', each associated with a specific keyword '{self.keyword}' and an accompanying description "{self.description}". These elements are sorted based on '{sort_metric}'.

        Please perform the following tasks:
        1. Review the '{data_type}' and keep only those that are directly relevant to the given keyword and its respective description. 
        2. Compare the description of each item in the '{data_type}' with the given description, and keep only those that are directly relevant to the give description.
        3. Format the filtered '{data_type}' into a visually appealing markdown unordered list. 
        4. Enhance the list's aesthetics and clarity for import into a markdown editor by adding an appropriate emoji next to each element, next to its '{sort_metric}' value.
        5. Ensure that the description of each item on the list is concise and coherent ideally 2-3 sentences long.
        "
        """
        return [
            {"role": "user", "content": prompt},
            {
                "role": "assistant",
                "content": f"Ok. Provide me with the unfiltered '{data_type}'.",
            },
        ]
