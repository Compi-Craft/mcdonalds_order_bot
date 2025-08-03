from dotenv import load_dotenv
import os
from mcdonalds_order_bot.menu_builder import create_menu

load_dotenv()

API_KEY = os.getenv("API_KEY")
MENU = create_menu()
