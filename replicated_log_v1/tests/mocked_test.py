import time

from app.master_node import MasterNode
from app.secondary_node import SecondaryNode
from tests.mocked_transport import MockedTransport


transport = MockedTransport()

secondary1 = SecondaryNode(transport)
secondary2 = SecondaryNode(transport)

master = MasterNode(
    transport=transport,
    secondaries=[secondary1, secondary2]
)


# m1: delay for the first secondary for 5 sec
transport.set_delay(master, secondary1, 5)

start = time.perf_counter()
master.append_message("m1")
elapsed = time.perf_counter() - start

assert master.list_messages() == ["m1"]
assert secondary1.list_messages() == ["m1"]
assert secondary2.list_messages() == ["m1"]
assert 5 <= elapsed < 6


# m2: delay for the second secondary for 6 sec
transport.set_delay(master, secondary2, 6)

start = time.perf_counter()
master.append_message("m2")
elapsed = time.perf_counter() - start

assert master.list_messages() == ["m1", "m2"]
assert secondary1.list_messages() == ["m1", "m2"]
assert secondary2.list_messages() == ["m1", "m2"]

assert 6 <= elapsed < 7


# m3: remove all delays and check
transport.remove_delay(master, secondary1)
transport.remove_delay(master, secondary2)

start = time.perf_counter()
master.append_message("m3")
elapsed = time.perf_counter() - start

assert master.list_messages() == ["m1", "m2", "m3"]
assert secondary1.list_messages() == ["m1", "m2", "m3"]
assert secondary2.list_messages() == ["m1", "m2", "m3"]

assert elapsed < 1


print("All tests passed")