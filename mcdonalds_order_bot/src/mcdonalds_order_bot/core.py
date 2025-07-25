from .ai_module import LLMClient

def main_loop():
    client = LLMClient()
    print("👋 Welcome to McDonald's! What can I get you started with?")
    while True:
        user_input = input("🧑 You: ")
        if user_input.lower() in ["exit", "quit", "that's all", "nothing more"]:
            print("✅ Thank you for your order!")
            break
        result = client.ask_llm(user_input)
        print("🤖 System parsed:")
        print(result)
