from pick import pick
from src.chapters import get_chapters
from src.download import get_input
from src.search import search_book
from os import system, name

cls = lambda: system("cls" if name == "nt" else "clear")
_, idx = pick(["Search book", "Download from URL", "Exit"], "Choose action:")
options = [search_book, get_input, exit]
res = options[idx]()

if res:
    cls()
    get_chapters(res)
