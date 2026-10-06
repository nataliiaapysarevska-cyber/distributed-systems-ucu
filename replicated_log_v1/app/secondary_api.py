from fastapi import FastAPI
from app.schema import Message
from app.secondary_node import SecondaryNode
from app.log_config import setup_logging
import os
import time

setup_logging()
app = FastAPI()

secondary = SecondaryNode()

DELAY = float(os.getenv("DELAY", "0"))
@app.post("/replicate")
def replicate_message(data: Message):
    if DELAY > 0:
        time.sleep(DELAY)

    secondary.append_message(data.message)
    return {"status": "ok"}


@app.get("/messages")
def get_messages():
    return secondary.list_messages()