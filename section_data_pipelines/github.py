import requests

from utils import timing


@timing
def get_github_search_results(keyword: str, count: int = 5) -> list[dict]:
    url = f"https://api.github.com/search/repositories?q={keyword}"
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
        return [{}]


if __name__ == "__main__":
    results = get_github_search_results("Auto-GPT")
    print(results)
