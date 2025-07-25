import openai
import instructor
from . import API_KEY
from .menu_builder import create_menu
from .models import Order

class LLMClient:

    def __init__(self):
        self.client = instructor.from_openai(openai.OpenAI(api_key = API_KEY))
        self.model = "gpt-4o-mini"
        self.temperature = 0.2
        self.repeat_times = 5
        self.menu = create_menu()
        self.system_prompt = self.build_system_prompt()
        self.messages = []

    def build_system_prompt(self):
        return f"""
You are a McDonald's virtual assistant. Your job is to extract structured order data from user messages.

--- MENU (YAML) ---
{self.menu}
-------------------

RULES:
- Only extract items that are present in the menu.
- A combo includes a burger, a drink and fries (both can be specified by user)
- Ingredients cannot be ordered standalone.
- Users can exclude ingredients or add extra ones.
- When modifying ingredients of a combo, specify them inside the "ingredients" object under the appropriate key, e.g. "ingredients": {{"burger": {{"excluded": [...], "extra": [...]}}}}.
- Do not place excluded or extra ingredients directly under the combo without specifying the target element (burger, drink, etc.).
- If the user mentions a virtual item (like "drink", "dessert", "burger") but does not specify the actual item (like "Coca-Cola", "Big Mac", etc.), treat it as a virtual item. Add its name (e.g. "drink") to the `virtual_items` list.
- Virtual items are separete from one in combo (adding drink to combo has nothing to do with virtual items and opposite)
- Output the full current order state as JSON matching the specified schema.
------------------
"""

    def ask_llm(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        chat_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        history = chat_history + self.messages
        response = self.client.chat.completions.create(
            model=self.model,
            max_retries=self.repeat_times,
            messages=history,
            temperature=0.2,
            response_model = Order
        )
        self.messages.append({"role": "assistant", "content": str(response.model_dump())})
        return response.model_dump()

        