import questionary
import requests
from urllib.parse import quote

from halo import Halo


def fetch_results(query: str, page: int = 1):
    """Fetch search results from the JSON API"""
    API_URL = "https://tokybook.com/api/v1/search"

    # Use pagination: each page gets 12 results
    offset = (page - 1) * 12
    limit = 12

    payload = {
        "query": query,
        "offset": offset,
        "limit": limit
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return {"content": [], "totalHits": 0}


def search_book(query: str = None, page: int = 1, previous_pages: dict = None, interactive: bool = True):
    if previous_pages is None:
        previous_pages = {}

    if query is None:
        query = input("Enter search query: ")

    spinner = Halo(text="Searching...", spinner="dots")
    spinner.start()

    if page in previous_pages:
        api_response = previous_pages[page]
    else:
        api_response = fetch_results(query, page)
        previous_pages[page] = api_response

    results = api_response.get("content", [])

    if not results:
        print("No results found. Exiting...")
        spinner.stop()
        return None

    # Extract titles and URLs from the JSON response
    # Assuming each book object has 'title' field and 'dynamicSlugId' for URL
    titles = []
    urls = []

    for book in results:
        title = book.get("title", "Unknown Title")
        book_id = book.get("bookId", book.get("dynamicSlugId", book.get("id", "")))
        if book_id:
            display_title = f"📖 {title}"
            titles.append(display_title)
            urls.append(book_id)

    # Check if there are more pages available
    current_offset = (page - 1) * 12
    total_results = api_response.get("totalHits", 0)
    has_more_results = current_offset + len(results) < total_results

    if has_more_results:
        titles.append("➡️ Next page")
        urls.append("next")

    if page > 1:
        titles.append("⬅️ Previous page")
        urls.append("previous")

    print("Search results:")
    for title in titles[:len(results)]:
        print(title)

    spinner.stop()

    if not interactive:
        if urls:
            return f"https://tokybook.com/post/{urls[0]}"
        else:
            return None

    titles.append("🔍 Search again")
    urls.append("search_again")
    titles.append("❌ Exit")
    urls.append("exit")

    choice = questionary.select("Search results:", choices=titles).ask()

    idx = titles.index(choice)

    if urls[idx] == "next":
        return search_book(query, page + 1, previous_pages, interactive)
    elif urls[idx] == "previous":
        return search_book(query, max(0, page - 1), previous_pages, interactive)
    elif urls[idx] == "search_again":
        return search_book(None, 1, {}, interactive)
    elif urls[idx] == "exit":
        print("Exiting...")
        return None

    # Return the full URL for the selected book
    selected_book_id = urls[idx]
    return f"https://tokybook.com/post/{selected_book_id}"
