from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)
class MasterNode:
    def __init__(self, transport, secondaries):
        self.transport = transport
        self.secondaries = secondaries
        self.messages = []
        self.executor = ThreadPoolExecutor(
            max_workers=max(1, len(secondaries))
        )

    def append_message(self, message: str):
        logger.info("Received message: %s", message)
        self.messages.append(message)
        replicated_tasks = []

        for secondary_url in self.secondaries:
            replicated_task = self.executor.submit(
                self.transport.send,
                self,
                secondary_url,
                message
            )
            replicated_tasks.append(replicated_task)

        for replicated_task in replicated_tasks:
            replicated_task.result()

        logger.info("Replication finished for message: %s", message)

    def list_messages(self):
        return list(self.messages)

