from pathlib import Path
import yaml

MENU_PATH = "./menu/{}"

def get_items(menu):
    filtered_items = []
    for item in menu.get('items', []):
        filtered_item = {}
        for key in ('name', 'category'):
            if key in item:
                filtered_item[key] = item[key]
        if 'properties' in item:
            filtered_item['properties'] = item['properties']

        filtered_items.append(filtered_item)
    return filtered_items

def get_combos(menu):
    filtered_items = []
    for item in menu.get('combos', []):
        filtered_item = {}
        key = 'name'
        if key in item:
            filtered_item[key] = item[key]
        filtered_items.append(filtered_item)
    return filtered_items

def get_virtual(menu):
    virtual_names = [
        item["name"]
        for item in menu.get("items", [])
        if item.get("virtual") is True
    ]

    return virtual_names

def get_ingredients(menu):
    ingredients = [
        item["name"]
        for item in menu.get("ingredients", [])
    ]

    return ingredients
    
def create_menu():
    new_menu = {}
    with open(MENU_PATH.format("menu_upsells.yaml"), "r") as f:
        menu = yaml.safe_load(f)
    new_menu['items'] = get_items(menu)
    new_menu['combos'] = get_combos(menu)
    with open(MENU_PATH.format("menu_virtual_items.yaml"), "r") as f:
        menu = yaml.safe_load(f)
    new_menu['virtuals'] = get_virtual(menu)
    with open(MENU_PATH.format("menu_ingredients.yaml"), "r") as f:
        menu = yaml.safe_load(f)
    new_menu['ingredients'] = get_ingredients(menu)
    return new_menu

def build_check_menu():
    default_menu = create_menu()
    items_lst = default_menu['items']
    check_menu = {}
    for item in items_lst:
        if item['category'] not in check_menu:
            check_menu[item['category']] = []
        check_menu[item['category']].append(item['name'])
    combo_list = default_menu['combos']
    check_menu['combos'] = []
    for combo in combo_list:
        check_menu['combos'].append(combo['name'])
    check_menu['virtuals'] = default_menu['virtuals']
    check_menu['ingredients'] = default_menu['ingredients']
    return check_menu

def ingredient_menu():
    with open(MENU_PATH.format("menu_ingredients.yaml"), "r") as f:
        menu = yaml.safe_load(f)
    result = {}
    for item in menu['items']:
        result[item['name']] = {"excluded": item['default_ingredients'],
                                "extra": item['possible_ingredients']}
    return result

def price_menu():
    with open(MENU_PATH.format("menu_upsells.yaml"), "r") as f:
        menu = yaml.safe_load(f)
    price_menu = {"items": {}, "ingredients": {}}
    for item in ["items", "combos"]:
        for product in menu[item]:
            price_menu['items'][product['name']] = product['price']
    with open(MENU_PATH.format("menu_ingredients.yaml"), "r") as f:
        menu = yaml.safe_load(f)
    for product in menu["ingredients"]:
        price_menu['ingredients'][product['name']] = product['price']
    return price_menu

if __name__ == "__main__":
    print(ingredient_menu())
