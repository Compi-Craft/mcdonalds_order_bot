from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import functools
from .order_manager import OrderManager

app = FastAPI()
clients = {}

templates = Jinja2Templates(directory="src/mcdonalds_order_bot/templates")
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def web_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(user_msg: dict):
    session_id = user_msg.get("session_id")
    user_input = user_msg.get("user_input")

    if not session_id or not user_input:
        raise HTTPException(status_code=400, detail="Missing session_id or user_input")

    if session_id not in clients:
        clients[session_id] = OrderManager()

    manager = clients[session_id]
    loop = asyncio.get_event_loop()
    bound_func = functools.partial(manager.chat_turn, user_input)
    response = await loop.run_in_executor(None, bound_func)

    return {"response": response, "state": manager.current_state, "session": session_id}
