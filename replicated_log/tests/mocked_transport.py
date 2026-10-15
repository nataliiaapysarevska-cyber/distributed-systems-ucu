import time


class MockedTransport:

    def __init__(self):
        self.delays = {}

    def set_delay(self, master, secondary, delay_seconds):
        self.delays[(master, secondary)] = delay_seconds

    def remove_delay(self, master, secondary):
        self.delays.pop((master, secondary), None)

    def send(self, master, secondary, message):
        delay = self.delays.get((master, secondary), 0)

        if delay > 0:
            time.sleep(delay)

        secondary.append_message(message)

        return True