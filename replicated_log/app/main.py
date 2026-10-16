from fastapi import FastAPI
import time

from app.master_node import MasterNode
from app.transport import HttpTransport
from app.schema import Message
from app.log_config import setup_logging
import os
from fastapi import HTTPException

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
    try:
        master.append_message(data.message, data.write_concern)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    t_end = time.perf_counter()
    return {"status": "ok", "time to response (s)": round(t_end - t_start, 3)}


@app.get("/messages")
def get_messages():
    return master.list_messages()
