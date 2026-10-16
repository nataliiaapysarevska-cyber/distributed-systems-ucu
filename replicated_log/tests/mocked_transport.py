import time
from threading import Event
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class MockedTransport:

    def __init__(self):
        self.delays = {}
        self.reorder_messages = {}
        self.buffer = {}
        self.reorder_events = {}
        self.lock = Lock()

    def set_delay(self, master, secondary, delay_seconds):
        self.delays[(master, secondary)] = delay_seconds

    def remove_delay(self, master, secondary):
        self.delays.pop((master, secondary), None)

    def set_reorder(self, master, secondary, messages_cnt):
        self.reorder_messages[(master, secondary)] = messages_cnt
        self.reorder_events[(master, secondary)] = Event()

    def remove_reorder(self, master, secondary):
        self.reorder_messages.pop((master, secondary), None)

    def send(self, master, secondary, message, sequence):
        key = (master, secondary)

        delay = self.delays.get(key, 0)

        if delay > 0:
            time.sleep(delay)

        has_reorder = False
        is_last_message = False
        messages_to_send = []

        with self.lock:
            reorder_messages_cnt = self.reorder_messages.get(key, 0)

            if reorder_messages_cnt > 0:
                has_reorder = True

                self.buffer.setdefault(key, [])
                self.buffer[key].append((message, sequence))

                if len(self.buffer[key]) == reorder_messages_cnt:
                    is_last_message = True

                    messages_to_send = sorted(self.buffer[key], key=lambda item: item[1], reverse=True)
                    self.buffer[key].clear()
                    self.remove_reorder(master, secondary)

        if not has_reorder:
            secondary.append_message(message, sequence)
            return True

        event = self.reorder_events[key]

        if is_last_message:
            for buffered_message, buffered_sequence in messages_to_send:
                secondary.append_message(
                    buffered_message,
                    buffered_sequence
                )

                logger.info("Reordering: sending message '%s' with seq_N=%s", buffered_message, buffered_sequence)

            event.set()

        else:
            if not event.wait(timeout=10):
                raise TimeoutError(
                    f"Reorder buffer was not filled for seq={sequence}"
                )

        return True
