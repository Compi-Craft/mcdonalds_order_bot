from .order_manager import OrderManager
import asyncio


async def user_input_loop(manager: OrderManager, shutdown_event: asyncio.Event):
    loop = asyncio.get_event_loop()
    while not shutdown_event.is_set():
        user_input = await loop.run_in_executor(None, input)
        await manager.queue.put(user_input)

async def chat_loop(manager: OrderManager, shutdown_event: asyncio.Event):
    while not shutdown_event.is_set():
        await manager.do_turn()

async def main_loop():
    shutdown_event = asyncio.Event()
    manager = OrderManager(shutdown_event)
    await asyncio.gather(
        user_input_loop(manager, shutdown_event),
        chat_loop(manager, shutdown_event)
    )
