from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import questionary
import requests

from rich.console import Console


@dataclass
class SearchResult:
    """Represents a single search result."""

    title: str
    book_id: str
    full_url: str


class SearchResultFormatter:
    """Handles formatting and display of search results."""

    @staticmethod
    def format_result(book: Dict[str, Any]) -> SearchResult:
        """Format a raw book dict into a SearchResult object."""
        title = book.get("title", "Unknown Title")
        book_id = book.get("bookId") or book.get("dynamicSlugId") or book.get("id") or ""
        full_url = f"https://tokybook.com/post/{book_id}" if book_id else ""
        return SearchResult(title, book_id, full_url)

    @staticmethod
    def get_display_choices(
        results: List[SearchResult], page: int, has_more: bool, has_previous: bool
    ) -> tuple:
        """Generate display choices for interactive selection."""
        titles = []
        urls = []

        for result in results:
            titles.append(f"📖 {result.title}")
            urls.append(result.book_id)

        # Add pagination options
        if has_more:
            titles.append("➡️ Next page")
            urls.append("next")

        if has_previous:
            titles.append("⬅️ Previous page")
            urls.append("previous")

        # Add interactive options
        titles.extend(["🔍 Search again", "❌ Exit"])
        urls.extend(["search_again", "exit"])

        return titles, urls


def fetch_results(query: str, page: int = 1) -> Dict[str, Any]:
    """Fetch search results from the JSON API."""
    API_URL = "https://tokybook.com/api/v1/search"

    offset = (page - 1) * 12
    limit = 12

    payload = {"query": query, "offset": offset, "limit": limit}

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return {"content": [], "totalHits": 0}


def search_book(query: Optional[str] = None, interactive: bool = True) -> Optional[str]:
    """Search for books using the API with iterative pagination instead of recursion."""
    current_page = 1
    api_cache: Dict[int, Dict[str, Any]] = {}

    while True:
        if query is None:
            query = input("Enter search query: ").strip()

        console = Console()

        # Show spinner while searching
        with console.status("[bold green]Searching...[/]", spinner="dots"):
            # Get cached or fetch results
            if current_page in api_cache:
                api_response = api_cache[current_page]
            else:
                api_response = fetch_results(query, current_page)
                api_cache[current_page] = api_response

        results = api_response.get("content", [])

        if not results:
            console.print("No results found. Exiting...")
            return None

        # Format results
        search_results = [
            SearchResultFormatter.format_result(book)
            for book in results
            if book.get("bookId") or book.get("dynamicSlugId")
        ]
        display_results = search_results

        # Check pagination
        current_offset = (current_page - 1) * 12
        total_results = api_response.get("totalHits", 0)
        has_more = current_offset + len(display_results) < total_results
        has_previous = current_page > 1

        # Display results
        console.print("Search results:")
        for i, result in enumerate(display_results, 1):
            console.print(f"{i}. 📖 {result.title}")

        if not interactive:
            return display_results[0].full_url if display_results else None

        # Get user choice
        formatter = SearchResultFormatter()
        choices, actions = formatter.get_display_choices(
            display_results, current_page, has_more, has_previous
        )

        choice = questionary.select("Choose action:", choices=choices).ask()

        if choice is None:
            print("No selection made. Exiting...")
            return None

        idx = choices.index(choice)
        action = actions[idx]

        if action == "next":
            current_page += 1
            continue
        elif action == "previous":
            current_page = max(1, current_page - 1)
            continue
        elif action == "search_again":
            query = None
            current_page = 1
            api_cache.clear()
            continue
        elif action == "exit":
            print("Exiting...")
            return None
        else:
            # Selected a book
            selected_result = next(r for r in display_results if r.book_id == action)
            return selected_result.full_url
