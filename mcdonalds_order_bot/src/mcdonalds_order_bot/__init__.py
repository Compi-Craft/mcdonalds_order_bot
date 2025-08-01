from dotenv import load_dotenv
import os
from mcdonalds_order_bot.menu_builder import create_menu

load_dotenv()


TRANSLATIONS = {
    "combo": "combos",
    "combos": "combos",
    "drink": "drinks",
    "burger": "burgers",
    "sauce": "sauces",
    "dessert": "desserts",
    "drinks": "drinks",
    "burgers": "burgers",
    "sauces": "sauces",
    "desserts": "desserts",
    "fries": "fries"
}

API_KEY = os.getenv("API_KEY")
MENU = create_menu()
