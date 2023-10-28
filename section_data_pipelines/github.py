import requests
from utils import timing
from bs4 import BeautifulSoup

BASE_URL = "https://github.com"


@timing
def get_github_search_results(keyword: str, count: int = 5) -> list[dict]:
    url = f"https://api.github.com/search/repositories?q={keyword}"
    return fetch_github_data(url, count)


@timing
def get_github_topic_results(topic: str, count: int = 5) -> list[dict]:
    url = f"https://api.github.com/search/repositories?q=topic:\"{topic}\"+is:featured"
    return fetch_github_data(url, count)


def fetch_github_data(url: str, count: int) -> list[dict]:
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        results = []

        for item in data["items"]:
            repo_info = {
                "link": item["html_url"],
                "description": item["description"],
                "stars": item["stargazers_count"],
            }
            results.append(repo_info)

        results = sorted(results, key=lambda x: x["stars"], reverse=True)
        return results[:count]
    else:
        print(f"Failed to get data, status code: {response.status_code}")
        return []


@timing
def get_github_collection_results(collection_id: str, count: int = 5) -> list[dict]:
    url = f"{BASE_URL}/collections/{collection_id}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for article in soup.select("article"):
            repo_link = article.select_one("h1.h3 a")["href"]
            stars_anchor = article.select_one('a[data-ga-click*="stargazers"]')
            if stars_anchor:
                stars_content = ''.join(filter(str.isdigit, stars_anchor.get_text()))
                stars = int(stars_content.strip()) if stars_content else 0
            else:
                stars = 0
            description = article.select_one("div.color-fg-muted").text.strip()
            results.append({
                "link": BASE_URL + repo_link,
                "stars": stars,
                "description": description
            })
        results = sorted(results, key=lambda x: x["stars"], reverse=True)
        return results[:count]
    else:
        print(f"Failed to get data, status code: {response.status_code}")
        return []


if __name__ == "__main__":
    # test_keyword = 'Auto-GPT'
    # search_results = get_github_search_results(test_keyword)
    # print(search_results)
    #
    # test_topic = '3d'
    # topic_results = get_github_topic_results(test_topic)
    # print(topic_results)

    test_collection_id = 'clean-code-linters'
    collection_results = get_github_collection_results(test_collection_id)
    print(collection_results)
