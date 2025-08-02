import openai
import instructor
from . import API_KEY, MENU
from .models import Order

class LLMClient:

    def __init__(self):
        self.client = instructor.from_openai(openai.OpenAI(api_key = API_KEY))
        self.model = "gpt-4o-mini"
        self.temperature = 0.2
        self.repeat_times = 5
        self.menu = MENU
        self.system_prompt = self.build_system_prompt()
        self.messages = []

    def build_system_prompt(self):
        return f"""
You are a McDonald's virtual assistant. Your job is to update current order state based on user message.

--- MENU ---
{self.menu}
-------------------

-------------------
RULES:
- Each request to you is independent, you should base only on current state
- Always fill all fields in responce (if you don't need to change anything for specific field, keep it from current state)
- ALWAYS COPY FROM CURRENT STATE this fields "combo_suggested", "sauce_suggested" - LEAVE THEM SAME AS IN CURRENT_STATE
- You will recive current order state and user input. You must update it based on user input
- It's okay to leave order state unchanged
- Use category names from menu only
- You should include only items from menu
- You have separeted field for "combo" with fries and drinks
- Asking large or small fries or drink for combo should change it's whole size to large or small accordingly
- If user don't specify drink for combo, leave it empty
- If user asks for combo or meal, use combo item structure with drink, fries and sause fields
- You will recive user input in current conversation field and history of messages in previous conversation field
- Don't include size if user didn't specified it clearly
- All virtual items have field named "virtual_items"
- If user asks for drink, burger etc (from virtuals list) and doesn'y clearly specify which one, add that to virtual_items field
- After user specifies item, it should be removed from virtuals
- If user mentions that it's end of order on current turn, or say's he doesn't want anything else, set 'finish_order" to true
- Ingredient can't be ordered as standallone items
- You can insert ingredients only from menu and they should be capitalized
------------------

--- User prompt structure ---
User input: current user request
Current state: current order state
Current conversation:  last system and user message
Previous conversation:  history of user/system conversation
------------------
"""

    def create_examples(self):
        return [
    {"role": "user", "content":
"""You should parse input of user to update current order state
User input: i want drink
Current state: {'items': [], 'virtual_items': [], 'finish_order': False}
Current conversation: ["👋 Welcome to McDonald's! What can I get you started with?", 'i want some drink']
Previous conversation: ["👋 Welcome to McDonald's! What can I get you started with?", 'i want some drink']"""},
    {"role": "assistant", "content": "{'items': [], 'virtual_items': [{'type': 'drink'}], 'finish_order': False}"},
    {"role": "user", "content": 
"""You should parse input of user to update current order state
User input: sprite
Current state - {'items': [], 'virtual_items': [{'type': 'drink'}], 'finish_order': False}
Current conversation - ['Please specify which drink do you want', 'sprite']
Previous conversation - ["👋 Welcome to McDonald's! What can I get you started with?", 'i want some drink', 'Please specify which drink do you want', 'sprite']"""},
    {"role": "assistant", "content": "{'items': [{'type': 'drink', 'name': 'Sprite', 'quantity': 1, 'size': None, 'ingredients': None, 'combo_suggested': False}], 'finish_order': False}"},
    {"role": "user", "content": 
"""You should parse input of user to update current order state
User input: no
Current state: {'items': [{'type': 'burger', 'name': 'Cheeseburger', 'quantity': 1, 'size': None, 'ingredients': None, 'combo_suggested': True}], 'virtual_items': [], 'finish_order': False}
Current conversation: ['Do you want to turn your Cheeseburger into combo?', 'no']
Previous conversation: ["👋 Welcome to McDonald's! What can I get you started with?", 'i want cheeseburger', 'Do you want to turn your Cheeseburger into combo?', 'no']
"""},
    {"role": "assistant", "content": "{'items': [{'type': 'burger', 'name': 'Cheeseburger', 'quantity': 1, 'size': None, 'ingredients': None, 'combo_suggested': True}], 'virtual_items': [], 'finish_order': False}"},
    {"role": "user", "content": 
"""You should parse input of user to update current order state
User input: i don't want tomatoes in my burger
Current state: {'items': [{'type': 'combos', 'name': 'Big Mac Meal', 'quantity': 1, 'fries': 'French Fries', 'drink': 'Coca-Cola', 'size': None, 'ingredients': None, 'sauce': None, 'sauce_suggested': False}], 'virtual_items': [], 'finish_order': False}
Current conversation: ['Do you want something else?', 'i don't want tomatoes in my burger']
Previous conversation: ["👋 Welcome to McDonald's! What can I get you started with?", 'i want big mac combo', 'Do you want something else?', 'i don't want tomatoes in my burger']
"""},
    {"role": "assistant", "content": "{'items': [{'type': 'combos', 'name': 'Big Mac Combo', 'quantity': 1, 'fries': 'French Fries', 'drink': 'Coca-Cola', 'size': 'medium', 'ingredients': {'burgers': {'excluded': ['Tomato'], 'extra': []}}, 'sauce': None, 'sauce_suggested': False}], 'virtual_items': [], 'finish_order': False}"}
        ]

    def create_chat_history(self):
        return [
            {"role": "system", "content": self.system_prompt}
        ]

    def ask_llm(self, current_conv, previous_conv, current_state):
        chat_history = self.create_chat_history() + self.create_examples()
        user_prompt = f"""You should parse input of user to update current order state
User input: {current_conv[1]}
Current state: {current_state}
Current conversation: {current_conv}
Previous conversation: {previous_conv}
"""
        request = {"role": "user", "content": user_prompt}
        chat_history.append(request)
        response = self.client.chat.completions.create(
            model=self.model,
            max_retries=self.repeat_times,
            messages=chat_history,
            temperature=self.temperature,
            response_model = Order
        )
        result = response.model_dump(exclude_unset=False)
        return result
