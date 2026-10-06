import logging

logger = logging.getLogger(__name__)
class SecondaryNode:
    def __init__(self, transport=None):
        self.messages = []

    def append_message(self, message: str):
        self.messages.append(message)
        logger.info("Secondary stored message: %s", message)

    def list_messages(self):
        return list(self.messages)
