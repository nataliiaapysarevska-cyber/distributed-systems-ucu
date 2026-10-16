import logging
from sortedcontainers import SortedDict
from threading import Lock

logger = logging.getLogger(__name__)


class SecondaryNode:
    def __init__(self, transport=None):
        self.messages = SortedDict()
        self.lock = Lock()
        self.last_sequence = 0

    def append_message(self, message: str, sequence: int):
        with self.lock:
            self.messages[sequence] = message
            logger.info("Secondary stored message: %s, seq_N=%s", message, sequence)

            while self.last_sequence + 1 in self.messages:
                self.last_sequence += 1

            if sequence > self.last_sequence:
                logger.info("seq_N=%s buffered, waiting for seq_N=%s", sequence, self.last_sequence + 1)

    def list_messages(self):
        with self.lock:
            return list(self.messages.values()[:self.last_sequence])
