import time

from app.master_node import MasterNode
from app.secondary_node import SecondaryNode
from tests.mocked_transport import MockedTransport
from concurrent.futures import ThreadPoolExecutor


print("--------Iteration 1 Synchronous replication: Tests started--------")
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
master.append_message("m1", 3)
elapsed = time.perf_counter() - start

assert master.list_messages() == ["m1"]
assert secondary1.list_messages() == ["m1"]
assert secondary2.list_messages() == ["m1"]
assert 5 <= elapsed < 6


# m2: delay for the second secondary for 6 sec
transport.set_delay(master, secondary2, 6)

start = time.perf_counter()
master.append_message("m2", 3)
elapsed = time.perf_counter() - start

assert master.list_messages() == ["m1", "m2"]
assert secondary1.list_messages() == ["m1", "m2"]
assert secondary2.list_messages() == ["m1", "m2"]

assert 6 <= elapsed < 7


# m3: remove all delays and check
transport.remove_delay(master, secondary1)
transport.remove_delay(master, secondary2)

start = time.perf_counter()
master.append_message("m3", 3)
elapsed = time.perf_counter() - start

assert master.list_messages() == ["m1", "m2", "m3"]
assert secondary1.list_messages() == ["m1", "m2", "m3"]
assert secondary2.list_messages() == ["m1", "m2", "m3"]

assert elapsed < 1


print("Iteration 1 Synchronous replication: All tests passed")

print("--------Iteration 2 Semi-Synchronous replication: Tests started--------")
print("\n--------Reordering check--------")
transport = MockedTransport()

secondary1 = SecondaryNode(transport)
secondary2 = SecondaryNode(transport)

master = MasterNode(
    transport=transport,
    secondaries=[secondary1, secondary2]
)

# m1: set reorder for secondary 1
print("Reorder messages for Secondary1 and wait 2 messages")
transport.set_reorder(master, secondary1, 2)
start = time.perf_counter()

with ThreadPoolExecutor(max_workers=4) as executor:
    m1_future = executor.submit(master.append_message, "m1", 3)
    m2_future = executor.submit(master.append_message, "m2", 3)
    m1_future.result()
    m2_future.result()

elapsed = time.perf_counter() - start

print("Master messages:", master.list_messages())
print("Secondary1 messages:", secondary1.list_messages())
print("Secondary2 messages:", secondary2.list_messages())
print("Time to replicate:",elapsed)

assert master.list_messages() == ["m1", "m2"]
assert secondary1.list_messages() == ["m1", "m2"]
assert secondary2.list_messages() == ["m1", "m2"]

print("--------Reordering check passed--------")
print("\n--------Eventual consistency check--------")

transport = MockedTransport()

secondary1 = SecondaryNode(transport)
secondary2 = SecondaryNode(transport)

master = MasterNode(
    transport=transport,
    secondaries=[secondary1, secondary2]
)

transport.set_delay(master, secondary2, 5)

master.append_message("m1", 1)

assert master.list_messages() == ["m1"]
assert secondary2.list_messages() == []

print("Temporary inconsistency:")
print("Master:", master.list_messages())
print("Secondary2:", secondary2.list_messages())

print("\nWaiting 5.5 seconds...\n")
time.sleep(5.5)
assert secondary2.list_messages() == ["m1"]

print("Eventually consistent:")
print("Master:", master.list_messages())
print("Secondary2:", secondary2.list_messages())

print("\n--------Eventual consistency check passed--------")
print("\n--------Iteration 2 Semi-Synchronous replication: All tests passed--------")