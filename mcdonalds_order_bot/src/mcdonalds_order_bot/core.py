from .order_manager import OrderManager
import asyncio


async def user_input_loop(manager: OrderManager):
    loop = asyncio.get_event_loop()
    while True:
        user_input = await loop.run_in_executor(None, input)
        await manager.queue.put(user_input)


async def main_loop():
    manager = OrderManager()

    await asyncio.gather(
        user_input_loop(manager),
        chat_loop(manager)
    )

async def chat_loop(manager: OrderManager):
    while True:
        await manager.do_turn()


