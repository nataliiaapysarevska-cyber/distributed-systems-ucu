from fastapi import FastAPI
import time

from app.master_node import MasterNode
from app.transport import HttpTransport
from app.schema import Message
from app.log_config import setup_logging
import os

setup_logging()
app = FastAPI()

SECONDARIES = [
    s.strip()
    for s in os.getenv(
        "SECONDARIES",
        "http://127.0.0.1:8001,http://127.0.0.1:8002"
    ).split(",")
    if s.strip()
]
transport = HttpTransport()
master = MasterNode(
    transport=transport,
    secondaries=SECONDARIES,
)


@app.post("/messages")
def add_message(data: Message):
    t_start = time.perf_counter()
    master.append_message(data.message)
    t_end = time.perf_counter()
    return {"status": "ok", "time to response (s)": round(t_end - t_start, 3)}


@app.get("/messages")
def get_messages():
    return master.list_messages()
