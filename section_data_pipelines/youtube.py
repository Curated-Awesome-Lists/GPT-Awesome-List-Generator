from youtubesearchpython import VideosSearch

from utils import timing


@timing
def search_youtube(keyword: str, limit: int = 5) -> list[dict]:
    videos_search = VideosSearch(keyword, limit=limit)
    results = videos_search.result()

    search_results = []
    for result in results["result"]:
        description_snippet = result.get("descriptionSnippet")
        search_results.append(
            {
                "title": result.get("title"),
                "link": result.get("link"),
                "description": description_snippet[0]["text"] if description_snippet else None,
                "views": result.get("viewCount")["short"],
            }
        )

    return search_results


if __name__ == "__main__":
    keyword = "Auto-GPT"
    videos = search_youtube(keyword)
    print(videos)
