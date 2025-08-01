from .order_manager import OrderManager
def main_loop():
    client = OrderManager()
    while True:
        client.do_turn()
