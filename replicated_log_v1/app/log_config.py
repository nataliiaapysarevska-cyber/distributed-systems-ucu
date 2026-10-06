import logging
import os

node_name = os.getenv("NODE_NAME", "node")
def setup_logging():
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s {node_name} %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/app.log", mode="w"),
        ],
        force=True,
    )