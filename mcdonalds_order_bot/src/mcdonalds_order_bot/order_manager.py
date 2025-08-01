from . import MENU, TRANSLATIONS
from .menu_builder import build_check_menu, ingredient_menu, price_menu
from .ai_module import LLMClient
import sys

class OrderManager:
    
    def __init__(self):
        self.current_state = {'items': [], 'virtual_items': [], 'finish_order': False}
        self.order = None
        self.asked_dessert = False
        self.state = "greeting"
        self.check_menu = build_check_menu()
        self.ingredient_menu = ingredient_menu()
        self.price_menu = price_menu()
        self.client = LLMClient()
        self.history = []

    def do_turn(self):
        if self.state == "greeting":
            self.send_message("👋 Welcome to McDonald's! What can I get you started with?")
        elif self.state == "validated":
            self.send_message("Do you want something else?")
        elif self.state == "finish":
            self.finish()
        else:
            self.send_message(self.state)

        if self.check_for_finish() is True:
            return

        msg = self.validate()            
        self.state = msg

    def check_for_finish(self):
        if self.state != "validated":
            self.order['finish_order'] = False
            return False
        if self.order['items'] == self.current_state['items'] and \
                self.order['virtual_items'] == self.current_state['virtual_items'] and \
                self.order['finish_order'] is True:
            self.current_state = self.order
            self.state = "finish"
            return True
        return False

    def validate(self):
        value, msg = self.basic_validation()
        if value is False:
            return msg
        value, msg = self.validate_combo()
        if value is False:
            return msg
        value, msg = self.validate_ingredients()
        if value is False:
            return msg
        self.current_state = self.order
        
        result, msg = self.ask_for_virtual()
        if result is False:
            return msg
        result, msg = self.suggestions()
        if result is False:
            return msg
        result, msg = self.check_size()
        if result is False:
            return msg
        if self.asked_dessert is False:
            res, msg = self.suggest_dessert()
            if res is False:
                return msg
        
        return "validated"

    def basic_validation(self):
        order = self.order['items']
        for item in order:
            item_type = item['type']
            if item_type not in TRANSLATIONS:
                return False, f"{item_type} is not valid product type"
            check_name = TRANSLATIONS[item_type]
            if item['name'] not in self.check_menu[check_name]:
                return False, f"{item['name']} is not valid product name"
        virtuals = self.order['virtual_items']
        for virtual in virtuals:
            naming = virtual['type']
            if naming not in self.check_menu['virtuals']:
                return False, f"{naming} is not valid virtual"
        return True, "validated"
    
    def validate_combo(self):
        order = self.order['items']
        for item in order:
            item_type = item['type']
            check_name = TRANSLATIONS[item_type]
            if check_name != "combos":
                continue
            if item['fries'] not in self.check_menu['fries']:
                return False, f"{item['fries']} is not valid fries for combo"
            if item['sauce'] and item['sauce'] not in self.check_menu['sauces']:
                return False, f"{item['sauce']} is not valid sauce for combo"
        return True, "combo validated"

    def suggestions(self):
        order = self.order['items']
        for item in order:
            item_type = item['type']
            check_name = TRANSLATIONS[item_type]
            if check_name == "combos" and item['sauce'] is None and item['sauce_suggested'] is False:
                item['sauce_suggested'] = True
                return False, f"Do want include some sauce to your {item['name']}?"
            if check_name == "burgers" and item['combo_suggested'] is False:
                item['combo_suggested'] = True
                return False, f"Do you want to turn your {item['name']} into combo?"
        return True, "validated"

    def suggest_dessert(self):
        order = self.order['items']
        for item in order:
            item_type = item['type']
            check_name = TRANSLATIONS[item_type]
            if check_name in ["combos", "burgers"]:
                self.asked_dessert=True
                return False, "Do you want some dessert?"
        return True, "validated"

    def check_size(self):
        order = self.order['items']
        for item in order:
            item_type = item['type']
            check_name = TRANSLATIONS[item_type]
            if check_name in ["drinks", "fries"] and item['size'] is None:
                return False, f"Pleasy specify size for {item['name']}"
            if check_name == "combos" and item['drink'] is None:
                return False, f"Pleasy specify drink for your {item['name']}"
        return True, "validated"

    def ask_for_virtual(self):
        order = self.order['virtual_items']
        for item in order:
            return False, f"Please specify which {item['type']} do you want"
        return True, "validated"

    def finish(self):
        total_sum = self.finalize()
        message = f"""Thank you for your order!
Total sum: {total_sum} $
Your order: {self.current_state}"""
        print("🤖 System: ", message)
        sys.exit(0)

    def show_order(self):
        pass

    def validate_ingredients(self):
        order = self.order['items']
        for item in order:
            item_type = item['type']
            check_name = TRANSLATIONS[item_type]
            if check_name == "combos":
                res, msg = self.validate_combo_ingredients(item)
                if res is False:
                    return res, msg
                continue
            ingredients = self.ingredient_menu[item['name']]
            item_ingredients = item['ingredients']
            missing = list(set(item_ingredients['extra']) - set(ingredients['extra']))
            if missing:
                return False, f"{', '.join(missing).strip(', ')} are not valid ingredients for {item['name']}"
            missing = list(set(item_ingredients['excluded']) - set(ingredients['excluded']))
            if missing:
                return False, f"{', '.join(missing).strip(', ')} are not valid ingredients for {item['name']}"
        return True, "validated"

    def validate_combo_ingredients(self, item):
        burger = ' '.join(item['name'].strip().split()[:-1])
        fries = item['fries']
        drink = item['drink']
        dct = {"burgers": burger, "fries": fries, "drinks": drink}
        for category, item_name in dct.items():
            if item_name is None:
                continue
            ingredients = self.ingredient_menu[item_name]
            item_ingredients = item['ingredients'][category]
            missing = list(set(item_ingredients['extra']) - set(ingredients['extra']))
            if missing:
                return False, f"{', '.join(missing).strip(', ')} are not valid ingredients for {item_name} in {item['name']}"
            if missing:
                return False, f"{', '.join(missing).strip(', ')} are not valid ingredients for {item_name} in {item['name']}"
        return True, "validated"

    def finalize(self):
        items = self.current_state['items']
        sum = 0
        sizes = {"small": 0.75, "medium": 1, "large": 1.25}
        for item in items:
            price = self.price_menu['items'][item['name']]
            if item['type'] == "combos":
                if item['sauce']:
                    price += self.price_menu['items'][item['sauce']]
                common_lst = item['ingredients']['burgers']['extra'] + item['ingredients']['drinks']['extra'] + item['ingredients']['fries']['extra']
                for ingredient in common_lst:
                    price += self.price_menu['ingredients'][ingredient]
            else:
                for ingredient in item['ingredients']['extra']:
                    price += self.price_menu['ingredients'][ingredient]
            if item['size'] and item['type'] in ['combos', 'drinks', 'fries']:
                price *= sizes[item['size']]
            sum += price
        return sum
    
    def check_deals(self):
        # TODO: "Check Deals"
        pass

    def send_message(self, message):
        print("🤖 System:", message)
        print("CURRENT STATE: ", self.current_state)
        self.history.append(message)
        user_input = input("🧑 You: ")
        self.history.append(user_input)
        self.order = self.client.ask_llm([message, user_input], self.history, self.current_state)
        print("LLM responce: ", self.order)
