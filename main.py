import questionary
from src.chapters import get_chapters
from src.download import get_input
from src.search import search_book
from os import system, name

cls = lambda: system('cls' if name == 'nt' else 'clear')

choices = [
    'Search book',
    'Download from URL',
    'Exit'
]

selected_action = questionary.select(
    "Choose action:",
    choices=choices
).ask()

options = [search_book, get_input, exit]
res = options[choices.index(selected_action)]()

if res:
    cls()
    get_chapters(res)