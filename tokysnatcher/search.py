import questionary
from urllib.parse import quote

from gazpacho import Soup, get
from halo import Halo


def fetch_results(query: str, page: int = 1):
    SEARCH_URL = f"https://tokybook.com/search/more?q={quote(query)}&page={page-1}"
    html = get(SEARCH_URL)
    soup = Soup(html)
    return soup


def search_book(query: str = None, page: int = 1, previous_pages: dict = None):
    if previous_pages is None:
        previous_pages = {}

    if query is None:
        query = input("Enter search query: ")

    spinner = Halo(text="Searching...", spinner="dots")
    spinner.start()

    if page in previous_pages:
        soup = previous_pages[page]
    else:
        soup = fetch_results(query, page)
        previous_pages[page] = soup

    results = soup.find("div", {"class": "book-card"})

    if not isinstance(results, list):
        print("No results found. Exiting...")
        spinner.stop()
        return None

    titles = [f"📖 {x.text}" for x in results]
    urls = [x.find("a").attrs.get("href") for x in results]

    next_page = len(results) == 10  # If we got 10 results, likely more pages exist
    if next_page:
        titles.append("➡️ Next page")
        urls.append("next")

    if page > 1:
        titles.append("⬅️ Previous page")
        urls.append("previous")

    spinner.stop()
    titles.append("🔍 Search again")
    urls.append("search_again")
    titles.append("❌ Exit")
    urls.append("exit")

    choice = questionary.select("Search results:", choices=titles).ask()

    idx = titles.index(choice)

    if urls[idx] == "next":
        return search_book(query, page + 1, previous_pages)
    elif urls[idx] == "previous":
        return search_book(query, max(0, page - 1), previous_pages)
    elif urls[idx] == "search_again":
        return search_book()
    elif urls[idx] == "exit":
        print("Exiting...")
        return None

    return f"https://tokybook.com{urls[idx]}"
