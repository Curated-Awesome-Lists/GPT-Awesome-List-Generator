import podsearch


def get_podcasts(keyword: str, max_results: int = 5) -> list[dict]:
    results = podsearch.search(keyword, country="us", limit=max_results)
    podcasts = []
    for result in results:
        podcast = {
            "title": result.name,
            "link": result.url,
            "description": f"Podcast by {result.author}. Category: {result.category}. "
            f"Number of episodes this year: {result.episode_count}",
        }
        podcasts.append(podcast)
    return podcasts


if __name__ == "__main__":
    keyword = "Chat GPT"
    podcasts = get_podcasts(keyword)
    print(podcasts)
