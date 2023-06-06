import requests
import pandas as pd


def get_github_search_results(keyword: str) -> pd.DataFrame:
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

        return pd.DataFrame(results)
    else:
        print(f"Failed to get data, status code: {response.status_code}")
        return pd.DataFrame()


if __name__ == "__main__":
    df = get_github_search_results("Auto-GPT")
    df = df.sort_values(by="stars", ascending=False)
    df = df.head(10)
    results = df.to_dict(orient="records")
    print(df)
