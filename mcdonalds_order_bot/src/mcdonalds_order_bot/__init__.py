from dotenv import load_dotenv
import os
from mcdonalds_order_bot.menu_builder import (
    create_menu,
    build_check_menu,
    ingredient_menu,
    price_menu,
    deals_menu
)

load_dotenv()

API_KEY = os.getenv("API_KEY")
MENU = create_menu()
CHECK_MENU = build_check_menu()
INGREDIENT_MENU = ingredient_menu()
PRICE_MENU = price_menu()
DEALS_MENU = deals_menu()
