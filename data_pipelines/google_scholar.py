import random
import re
import time

import requests
from bs4 import BeautifulSoup


def scrape_google_scholar(keyword, num_results=100):
    """Scrapes Google Scholar for search results for the specified keyword.

    Args:
      keyword: The keyword to search for.
      num_results: The desired number of results. Default is 100.

    Returns:
      A list of dictionaries, each representing a search result. Each dictionary
      contains the title, brief description, link, and number of citations for the
      search result.
    """

    results = []
    start = 0

    while len(results) < num_results:
        url = f"https://scholar.google.com/scholar?hl=en&q={keyword}&start={start}"
        response = requests.get(url)
        time.sleep(random.uniform(1, 3))
        soup = BeautifulSoup(response.content, "html.parser")

        for result in soup.find_all("div", class_="gs_ri"):
            title = result.find("h3", class_="gs_rt").text
            description = result.find("div", class_="gs_rs").text
            link = (
                result.h3.a["href"]
                if result.h3.a and "href" in result.h3.a.attrs
                else ""
            )

            # Use regex to find the "Cited by" link
            citations = result.find("a", text=re.compile(r"Cited by"))
            if citations:
                citations_text = citations.text
                cited_by = int(re.search(r"\d+", citations_text).group())
            else:
                cited_by = 0

            result_dict = {
                "title": title,
                "description": description,
                "link": link,
                "citations": cited_by,
            }
            results.append(result_dict)

            if len(results) >= num_results:
                break

        # Go to the next page of results
        start += 10
    results = results[:num_results]

    return results


if __name__ == "__main__":
    scholar_dict = scrape_google_scholar("Auto-GPT")
    print(scholar_dict)
