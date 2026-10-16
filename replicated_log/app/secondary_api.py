from fastapi import FastAPI
from app.schema import ReplicatedMessage
from app.secondary_node import SecondaryNode
from app.log_config import setup_logging
import os
import time
import logging

logger = logging.getLogger(__name__)

setup_logging()
app = FastAPI()

secondary = SecondaryNode()

DELAY = float(os.getenv("DELAY", "0"))


@app.post("/replicate")
def replicate_message(data: ReplicatedMessage):
    if DELAY > 0:
        logger.info("Replication delay: sleeping %s seconds for seq_N=%s", DELAY, data.sequence)
        time.sleep(DELAY)

    secondary.append_message(data.message, data.sequence)
    return {"status": "ok"}


@app.get("/messages")
def get_messages():
    return secondary.list_messages()
