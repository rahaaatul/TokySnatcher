from urllib.parse import quote

from gazpacho import Soup, get
from halo import Halo
from pick import pick


def fetch_results(query: str, page: int = 1):
    SEARCH_URL = f"https://tokybook.com/page/{page}/?s="
    html = get(SEARCH_URL + quote(query))
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

    not_found = soup.find("h1", {"class": "entry-title"})

    if not_found and not_found.text == "Nothing Found":
        print("No results found!")
        spinner.stop()
        return search_book()

    results = soup.find("h2", {"class": "entry-title"})

    if not isinstance(results, list):
        print("No results found. Exiting...")
        spinner.stop()
        return None

    titles = [f"📖 {x.text}" for x in results]
    urls = [x.find("a").attrs.get("href") for x in results]

    next_page = soup.find("a", {"class": "next page-numbers"})
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

    _, idx = pick(titles, "Search results:", indicator="*")

    if urls[idx] == "next":
        return search_book(query, page + 1, previous_pages)
    elif urls[idx] == "previous":
        return search_book(query, page - 1, previous_pages)
    elif urls[idx] == "search_again":
        return search_book()
    elif urls[idx] == "exit":
        print("Exiting...")
        return None

    return urls[idx]
