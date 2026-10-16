from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class MasterNode:
    def __init__(self, transport, secondaries):
        self.transport = transport
        self.secondaries = secondaries
        self.messages = []
        self.sequence = 0
        self.lock = Lock()
        self.executor = ThreadPoolExecutor(
            max_workers=max(1, len(secondaries) * 5)
        )

    def append_message(self, message: str, w: int):
        if w <= 0 or w > len(self.secondaries) + 1:
            raise ValueError(f"Write concern must be between 1 and {len(self.secondaries) + 1}")
        with self.lock:
            self.sequence += 1
            sequence = self.sequence
            logger.info("Received message: %s, seq_N=%s, write_concern=%s", message, sequence, w)
            self.messages.append({"sequence": sequence, "message": message})

        replicated_tasks = []
        required_secondary_acks = w - 1

        acks = 0
        for secondary_url in self.secondaries:
            replicated_task = self.executor.submit(
                self.transport.send,
                self,
                secondary_url,
                message,
                sequence
            )
            replicated_tasks.append(replicated_task)

        if required_secondary_acks == 0:
            logger.info("Write concern satisfied for seq_N=%s: no Secondary ACK required, return response to Client", sequence)
            return

        for replicated_task in as_completed(replicated_tasks):
            try:
                replicated_task.result()
                acks += 1
                logger.info(
                    "ACK received for seq_N=%s: %s/%s required Secondary ACKs", sequence, acks, required_secondary_acks)
            except Exception as e:
                logger.error("Failed to ack message: %s", e)

            if acks == required_secondary_acks:
                break
        if acks < required_secondary_acks:
            raise RuntimeError(
                f"Write concern not satisfied: "
                f"required {required_secondary_acks} secondary ACKs, got {acks}"
            )

        logger.info("Write concern satisfied for seq_N=%s, message=%s", sequence, message)

    def list_messages(self):
        with self.lock:
            return [item["message"] for item in self.messages]
