import re

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


def scrape_google_scholar(keyword: str) -> list[dict]:
    url = "https://scholar.google.com/scholar?q=" + keyword

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    search_results = soup.find_all("div", {"class": "gs_ri"})

    data = []
    for result in search_results:
        title = result.h3.text if result.h3 else ""
        link = result.h3.a["href"] if result.h3.a and "href" in result.h3.a.attrs else ""
        description = (
            result.find("div", {"class": "gs_rs"}).text
            if result.find("div", {"class": "gs_rs"})
            else ""
        )
        citation_info = (
            result.find("div", {"class": "gs_fl"}).text
            if result.find("div", {"class": "gs_fl"})
            else ""
        )

        # Extract citation count from the citation info
        citation_count_match = re.search(r"Cited by (\d+)", citation_info)
        citation_count = (
            int(citation_count_match.group(1)) if citation_count_match else np.nan
        )

        data.append([title, link, description, citation_count])

    df = pd.DataFrame(data, columns=["Title", "Link", "Description", "Citation Count"])
    df = df.dropna(axis=1, how="all")
    return df.to_dict(orient="records")


if __name__ == "__main__":
    scholar_dict = scrape_google_scholar("Auto-GPT")
    print(scholar_dict)
