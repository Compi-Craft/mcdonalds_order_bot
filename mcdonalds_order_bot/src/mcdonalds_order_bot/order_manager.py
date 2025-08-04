from . import CHECK_MENU, INGREDIENT_MENU, PRICE_MENU, DEALS_MENU
from .ai_module import LLMClient
import functools
import asyncio
from itertools import zip_longest

class OrderManager:
    
    def __init__(self, shutdown_event = None):
        self.current_state = {'items': [], 'virtual_items': [], 'deals': [], 'finish_order': False}
        self.order = None
        self.asked_dessert = False
        self.state = "greeting"
        self.check_menu = CHECK_MENU
        self.ingredient_menu = INGREDIENT_MENU
        self.price_menu = PRICE_MENU
        self.deals_menu = DEALS_MENU
        self.client = LLMClient()
        self.history = []
        self.queue = asyncio.Queue()
        self.shutdown_event = shutdown_event

    async def do_turn(self):
        if self.state == "greeting":
            await self.send_message("👋 Welcome to McDonald's! What can I get you started with?")
        elif self.state == "validated":
            await self.send_message("Do you want something else?")
        elif self.state == "finish":
            self.finish(True)
            return
        else:
            await self.send_message(self.state)

        if self.check_for_finish():
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
        value, msg = self.validate_double_deal()
        if value is False:
            return msg
        self.current_state = self.order
        
        result, msg = self.ask_for_virtual()
        if result is False:
            return msg
        result, msg = self.check_size()
        if result is False:
            return msg
        result, msg = self.check_deals()
        if result is False:
            return msg
        result, msg = self.suggestions()
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
            check_name = item['type']
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
            check_name = item['type']
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
            check_name = item['type']
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
            if item['type'] == "desserts":
                self.asked_dessert = True
                return True, "validated"
        for item in order:
            check_name = item['type']
            if check_name in ["combos", "burgers"]:
                self.asked_dessert=True
                return False, "Do you want some dessert?"
        return True, "validated"

    def check_size(self):
        order = self.order['items']
        for item in order:
            check_name = item['type']
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
    
    def show_order(self):
        order_str = ""
        combo_template = """
Combo: {}
Ingrediends added to burger: {}
Ingredients excluded from burger: {}
Quantity: {}
Size: {}
Fries: {}
Ingrediends added: {}
Ingredients excluded: {}
Drink: {}
Ingrediends added: {}
Ingredients excluded: {}
Sauce: {}

"""
        size_item_template = """
{}
Quantity: {}
Size: {}
Ingrediends added: {}
Ingredients excluded: {}

"""
        item_template = """
{}
Quantity: {}
Ingrediends added: {}
Ingredients excluded: {}

"""
        print(self.current_state)
        for item in self.current_state['items']:
            if item['type'] == "combos":
                order_str += combo_template.format(
                    item['name'], 
                    item['ingredients']['burgers']['extra'],
                    item['ingredients']['burgers']['excluded'],
                    item['quantity'],
                    item['size'],
                    item['fries'],
                    item['ingredients']['fries']['extra'],
                    item['ingredients']['fries']['excluded'],
                    item['drink'],  
                    item['ingredients']['drinks']['extra'],
                    item['ingredients']['drinks']['excluded'],
                    item['sauce']
                    )
            elif item['type'] in ["drinks", "fries"]:
                order_str += size_item_template.format(
                    item['name'],
                    item['quantity'],
                    item['size'],
                    item['ingredients']['extra'],
                    item['ingredients']['excluded']
                )
            else:
                print(item)
                order_str += item_template.format(
                    item['name'],
                    item['quantity'],
                    item['ingredients']['extra'],
                    item['ingredients']['excluded']
                )
        for deal in self.current_state['deals']:
            for item in deal.values():
                order_str += item_template.format(
                    item['name'],
                    1,
                    item['ingredients']['extra'],
                    item['ingredients']['excluded']
                )
        return order_str

    def finish(self, stop = False):
        total_sum = self.finalize()
        message = f"""Thank you for your order!
Total sum: {total_sum} $
Your order: 
{self.show_order()}
"""
        print("🤖 System: ", message)
    
        if stop and self.shutdown_event:
            self.shutdown_event.set()

    def validate_ingredients(self):
        order = self.order['items']
        for item in order:
            check_name = item['type']
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
        for deal in self.order['deals']:
            for item in deal.values():
                if item is None:
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

    def count_burgers(self):
        burger_lst = {'Small Double Deal': [], 'Big Double Deal': []}
        for item in self.current_state['items']:
            if item['type'] != "burgers":
                continue
            item['price'] = self.price_menu['items'][item['name']]
            if item['name'] in self.deals_menu['Small Double Deal']:
                burger_lst['Small Double Deal'].append(item)
            else:
                burger_lst['Big Double Deal'].append(item)

        for key, dct in burger_lst.items():
            dct.sort(key=lambda x: x["price"], reverse=True)
            burger_lst[key] = list(zip_longest(dct[::2], dct[1::2]))
        print(burger_lst)
        total_sum = 0
        for dct in burger_lst.values():
            for value in dct:
                if value[1] is None:
                    for ingredient in value[0]['ingredients']['extra']:
                        total_sum += self.price_menu['ingredients'][ingredient]
                    total_sum += value[0]['price']
                else:
                    price = 0
                    for ingredient in value[0]['ingredients']['extra']:
                        price += self.price_menu['ingredients'][ingredient]
                    for ingredient in value[1]['ingredients']['extra']:
                        price += self.price_menu['ingredients'][ingredient]
                    price += value[0]['price'] + value[1]['price']
                    price *= 0.8
                    total_sum += price
        return total_sum

    def finalize(self):
        items = self.current_state['items']
        sum = 0
        sizes = {"small": 0.75, "medium": 1, "large": 1.25}
        sum += self.count_burgers()
        for item in items:
            if item['type'] == "burgers":
                continue
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
        double_deal_sum = 0
        for deal in self.order['deals']:
            for item in deal.values():
                price = self.price_menu['items'][item['name']]
                for ingredient in item['ingredients']['extra']:
                    price += self.price_menu['ingredients'][ingredient]
                double_deal_sum += price * 0.8
        sum += double_deal_sum
        return sum
    
    def check_deals(self):
        deals = self.order['deals']
        for deal in deals:
            burger1, burger2 = deal['burger1'], deal['burger2']
            if burger1 is None and burger2 is None:
                return False, "Please specify burgers for your double deal"
            if burger1 is None:
                return False, f"You've already ordered {burger2['name']} for your double deal, please specify second burger for your double deal"
            if burger2 is None:
                return False, f"You've already ordered {burger1['name']} for your double deal, please specify second burger for your double deal"
        return True, "validated"

    def validate_double_deal(self):
        deals = self.order['deals']
        for deal in deals:
            burger1, burger2 = deal['burger1'], deal['burger2']
            if burger1 is None or burger2 is None:
                continue
            flag = False
            for check_lst in self.deals_menu.values():
                if burger1['name'] in check_lst and burger2['name'] in check_lst:
                    flag = True
                    break
            if flag is False:
                return False, f"{burger1['name']} and {burger2['name']} is wrong pair for double deal"
        return True, "validated"

    async def send_message(self, message):
        print("🤖 System:", message)
        print("CURRENT STATE: ", self.current_state)
        self.history.append(message)

        user_input = await self.queue.get()
        self.history.append(user_input)

        loop = asyncio.get_event_loop()
        bound_func = functools.partial(
            self.client.ask_llm,
            [message, user_input],
            self.history,
            self.current_state
        )
        self.order = await loop.run_in_executor(None, bound_func)
        print("LLM response:", self.order)

    def chat_turn(self, user_input: str) -> str:
        if self.state == "finish":
            return "Order is already finished."

        if self.state == "greeting":
            system_msg = "👋 Welcome to McDonald's! What can I get you started with?"
        elif self.state == "validated":
            system_msg = "Do you want something else?"
        else:
            system_msg = self.state
        self.history.append(system_msg)
        self.history.append(user_input)
        self.order = self.client.ask_llm([system_msg, user_input], self.history, self.current_state)
        if self.check_for_finish():
            self.state = "finish"
            total_sum = self.finalize()
            return f"Thank you for your order!\nTotal sum: {total_sum} $\nYour order: \n{self.show_order()}"
        msg = self.validate()
        self.state = msg
        if msg == "validated":
            return "Do you want something else?"
        return msg
