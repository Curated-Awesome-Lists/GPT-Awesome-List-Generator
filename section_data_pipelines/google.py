import os

import requests
from enum import Enum


class SearchMode(Enum):
    ARTICLES = "articles"
    COURSES = "courses"
    BOOKS = "books"
    RESEARCH = "research"
    PODCASTS = "podcasts"
    VIDEOS = "videos"
    TOOLS_SOFTWARE = "tools_software"
    CONFERENCES_EVENTS = "conferences_events"
    SLIDES_PRESENTATIONS = "slides_presentations"


websites_to_search_articles = [
    "medium.com",  # Medium
    "dev.to",  # The DEV Community
    "hackernoon.com",  # Hacker Noon
    "smashingmagazine.com",  # Smashing Magazine
    "alistapart.com",  # A List Apart
    "dzone.com",  # DZone
    "infoq.com",  # InfoQ
    "tutsplus.com",  # Tuts+ (from Envato Tuts+)
    "css-tricks.com",  # CSS-Tricks
    "sitepoint.com",  # SitePoint
    "tympanus.net/codrops",  # Codrops
    "realpython.com",  # Real Python
    "freecodecamp.org/news",  # Freecodecamp News
    "towardsdatascience.com",  # Towards Data Science (Medium's Data Science community)
    "arxiv.org",  # arXiv (Research Papers in AI, ML, CS, etc.)
    "ai.googleblog.com",  # Google AI Blog
    "blogs.nvidia.com",  # NVIDIA Blog (AI, Deep Learning)
    "distill.pub",  # Distill (ML Visualization)
    "deepmind.com/blog",  # DeepMind Blog
    "openai.com/blog",  # OpenAI Blog
    "neuralink.com/blog",  # Neuralink Blog
    "research.fb.com",  # Facebook AI Research Blog
    "research.google",  # Google Research Publications
    "blogs.microsoft.com/ai",  # Microsoft AI Blog
    "blog.tensorflow.org",  # TensorFlow Blog
    "pytorch.org/blog",  # PyTorch Blog
    "blog.ycombinator.com",  # Y Combinator Blog (Startups, Tech News)
    "thenewstack.io",  # The New Stack (Cloud, Containers, etc.)
    "overleaf.com/learn",  # Overleaf (LaTeX, Research Writing)
    "geeksforgeeks.org",  # GeeksforGeeks (CS, Algorithms, Tutorials)
    "stackoverflow.blog",  # Stack Overflow Blog
    "martinfowler.com",  # Martin Fowler's Blog (Software Design, Patterns)
    "acm.org/technews",  # ACM TechNews
    "spectrum.ieee.org/computing"  # IEEE Spectrum's computing section
]

websites_to_search_courses = [
    "udemy.com",
    "coursera.org",
    "edx.org",
    "pluralsight.com",
    "khanacademy.org",
    "lynda.com",
    "udacity.com",
    "codecademy.com",
    "futurelearn.com",
    "skillshare.com"
    "linkedin.com/learning",
]

websites_to_search_books = [
    "amazon.com",
    "goodreads.com",
    "barnesandnoble.com",
    "books.google.com",
    "bookdepository.com",
    "powells.com",
    "abebooks.com",
    "springer.com",
    "oreilly.com",
    "packtpub.com"
]

websites_to_search_research = [
    "scholar.google.com",
    "semanticscholar.org",
    "jstor.org",
    "springer.com",
    "ieee.org",
    "sciencedirect.com",
    "researchgate.net",
    "pubmed.ncbi.nlm.nih.gov",
    "arxiv.org",
    "ncbi.nlm.nih.gov"
]

websites_to_search_podcasts = [
    "anchor.fm",
    "stitcher.com",
    "podbean.com",
    "spotify.com",
    "itunes.apple.com",
    "podbay.fm",
    "podtail.com",
    "podcasts.apple.com",
    "player.fm",
    "overcast.fm"
]

websites_to_search_videos = [
    "youtube.com",
    "vimeo.com",
    "twitch.tv",
    "ted.com",
    "dailymotion.com",
]

websites_to_search_tools_software = [
    "alternativeto.net",
    "producthunt.com",
    "capterra.com",
    "sourceforge.net",
    "softpedia.com",
    "g2.com"
]

websites_to_search_conferences_or_events = [
    "eventbrite.com",
    "meetup.com",
    "10times.com",
    "conferenceseries.com",
    "techmeme.com/events",  # for tech-related events
    "lanyrd.com"
]

websites_to_search_slides_or_presentations = [
    "slideshare.net",
    "speakerdeck.com",
    "academia.edu",  # Some researchers share their presentations here
    "prezi.com",
    "slideboom.com",
    "authorstream.com"
]

websites_to_search = {
    SearchMode.ARTICLES: websites_to_search_articles,
    SearchMode.COURSES: websites_to_search_courses,
    SearchMode.BOOKS: websites_to_search_books,
    SearchMode.RESEARCH: websites_to_search_research,
    SearchMode.PODCASTS: websites_to_search_podcasts,
    SearchMode.VIDEOS: websites_to_search_videos,
    SearchMode.TOOLS_SOFTWARE: websites_to_search_tools_software,
    SearchMode.CONFERENCES_EVENTS: websites_to_search_conferences_or_events,
    SearchMode.SLIDES_PRESENTATIONS: websites_to_search_slides_or_presentations
}

terms_to_search = {
    SearchMode.ARTICLES: "(article OR blog OR tutorial OR guide OR post)",
    SearchMode.COURSES: "(course OR tutorial OR class OR certification OR training)",
    SearchMode.BOOKS: "(book OR ebook OR textbook OR manual)",
    SearchMode.RESEARCH: "(paper OR article OR publication OR study OR research)",
    SearchMode.PODCASTS: "(podcast OR episode OR show OR series OR audio)",
    SearchMode.VIDEOS: "(video OR lecture OR webinar)",
    SearchMode.TOOLS_SOFTWARE: "(software OR tool OR utility OR app OR platform OR service)",
    SearchMode.CONFERENCES_EVENTS: "(conference OR event OR workshop OR seminar OR symposium OR tech talk)",
    SearchMode.SLIDES_PRESENTATIONS: "(slides OR presentation OR deck OR ppt OR powerpoint OR keynote)"
}


def search_google(keyword: str, mode: SearchMode = SearchMode.ARTICLES, max_results: int = 10):
    global websites_to_search
    global terms_to_search
    api_key = os.environ["GOOGLE_CLOUD_API_KEY"]
    cse_id = os.environ["CUSTOM_SEARCH_ENGINE_ID"]

    # Create a combined query with the "site:" search operator
    base_query = f"{keyword}"
    base_query += " " + terms_to_search[mode]
    site_specific_queries = " OR ".join([f"site:{site}" for site in websites_to_search[mode]])
    query = f"{base_query} {site_specific_queries}"

    # Endpoint for Google Custom Search
    url = "https://www.googleapis.com/customsearch/v1"

    all_items = []
    pages = -(-max_results // 10)  # This is a ceiling division trick

    for page in range(pages):
        start_index = page * 10 + 1

        # Parameters for the search query
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': query,
            'num': 10 if (max_results - len(all_items)) > 10 else (max_results - len(all_items)),
            # fetch remaining if less than 10
            'start': start_index
        }

        # Make the API request
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            results = response.json()

            # Extract the desired data
            for item in results.get('items', []):
                page_map = item.get('pagemap', {})
                og_description = page_map.get('metatags', [{}])[0].get('og:description', '')
                all_items.append({
                    'title': item['title'],
                    'link': item['link'],
                    'description': item['snippet'] + ' ' + og_description
                })
        else:
            print(f"Error {response.status_code}: {response.text}")
            break

        if len(all_items) >= max_results:
            break

    return all_items


def search_google_for_articles(keyword: str, max_results: int = 10):
    return search_google(keyword, SearchMode.ARTICLES, max_results)


def search_google_for_courses(keyword: str, max_results: int = 10):
    return search_google(keyword, SearchMode.COURSES, max_results)


def search_google_for_books(keyword: str, max_results: int = 10):
    return search_google(keyword, SearchMode.BOOKS, max_results)


def search_google_for_research(keyword: str, max_results: int = 10):
    return search_google(keyword, SearchMode.RESEARCH, max_results)


def search_google_for_podcasts(keyword: str, max_results: int = 10):
    return search_google(keyword, SearchMode.PODCASTS, max_results)


def search_google_for_videos(keyword: str, max_results: int = 10):
    return search_google(keyword, SearchMode.VIDEOS, max_results)


def search_google_for_tools_software(keyword: str, max_results: int = 10):
    return search_google(keyword, SearchMode.TOOLS_SOFTWARE, max_results)


def search_google_for_conferences_or_events(keyword: str, max_results: int = 10):
    return search_google(keyword, SearchMode.CONFERENCES_EVENTS, max_results)


def search_google_for_slides_or_presentations(keyword: str, max_results: int = 10):
    return search_google(keyword, SearchMode.SLIDES_PRESENTATIONS, max_results)


if __name__ == "__main__":
    search_query = 'Auto-GPT'
    articles = search_google(search_query)
    # Print the results
    for article in articles:
        print(article['title'])
        print(article['link'])
        print(article['description'])
        print('-' * 80)
