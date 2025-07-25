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
        for key in ('name', 'category'):
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

if __name__ == "__main__":
    create_menu()
