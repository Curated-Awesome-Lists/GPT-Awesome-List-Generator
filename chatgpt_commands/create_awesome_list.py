from typing import List

from connections import github, google_scholar


def get_create_awsome_list_command(
    keyword: str, projects: List[dict], papers: List[dict]
) -> str:
    command = f""" create an 'awesome list' on {keyword} that I plan to share publicly
    . It should be a diverse mix of resources that cater to a wide 
    range of audiences, from beginners to experts.

    Here's a list of dicts of the projects and papers that I've recently found and 
    could be included:
    1. Project: {projects} \n
    2. Paper: {papers} \n
    
    Send me your answer as a Markdown code. Don't say sure or yes, just send me the code."""
    return command


if __name__ == "__main__":
    keyword = "AWS"
    projects_df = github.get_github_search_results(keyword)
    projects_df = projects_df.sort_values(by="stars", ascending=False)
    projects_df = projects_df.head(5)
    projects = projects_df.to_dict("records")

    # papers_df = google_scholar.scrape_google_scholar(keyword)
    # papers_df = papers_df.sort_values(by="Citation Count", ascending=False)
    # papers_df = papers_df.head(10)
    # papers = papers_df.to_dict("records")

    command = get_create_awsome_list_command(keyword, projects, [{}])
    print(command)
