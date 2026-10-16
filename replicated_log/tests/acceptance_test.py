import os
import time

import httpx
from concurrent.futures import ThreadPoolExecutor

MASTER_URL = os.getenv("MASTER_URL", "http://127.0.0.1:8000")
SECONDARY_URL_1 = os.getenv("SECONDARY_URL_1", "http://127.0.0.1:8001")
SECONDARY_URL_2 = os.getenv("SECONDARY_URL_2", "http://127.0.0.1:8002")


def post_message(message, w):
    return httpx.post(
        f"{MASTER_URL}/messages",
        json={"message": message, "write_concern": w},
        timeout=15,
    )


def get_messages(node):
    return httpx.get(f"{node}/messages").json()


print("--------Iteration 2 Semi-Synchronous replication: Acceptance tests started--------")
print("------(Msg1, W=1)------")

start = time.perf_counter()
response1 = post_message("Msg1", 1)
elapsed = time.perf_counter() - start

print(f"Message 1 took {elapsed:.3f} seconds")
print(f"Master messages: {get_messages(MASTER_URL)}")
print(f"Secondary1 messages: {get_messages(SECONDARY_URL_1)}")
print(f"Secondary2 messages: {get_messages(SECONDARY_URL_2)}")

assert response1.status_code == 200
assert get_messages(MASTER_URL) == ["Msg1"]

print("------(Msg2, W=2)------")
start = time.perf_counter()

response2 = post_message("Msg2", 2)
elapsed = time.perf_counter() - start

print(f"Message 2 took {elapsed:.3f} seconds")
print(f"Master messages: {get_messages(MASTER_URL)}")
print(f"Secondary1 messages: {get_messages(SECONDARY_URL_1)}")
print(f"Secondary2 messages: {get_messages(SECONDARY_URL_2)}")

assert response2.status_code == 200
assert get_messages(MASTER_URL) == ["Msg1", "Msg2"]
assert get_messages(SECONDARY_URL_1) == ["Msg1", "Msg2"]

print("------(Msg3, W=3) & (Msg4, W=1)------")
start3 = time.perf_counter()
executor = ThreadPoolExecutor(max_workers=2)
print("------(Msg3, W=3) send------")
msg3_future = executor.submit(post_message, "Msg3", 3,)
time.sleep(0.1)
print("------(Msg4, W=1) send------")
start4 = time.perf_counter()
msg4_future = executor.submit(post_message, "Msg4", 1)
response4 = msg4_future.result()

elapsed4 = time.perf_counter() - start4
print(f"Message 4 took {elapsed4:.3f} seconds")
print(f"Master messages: {get_messages(MASTER_URL)}")
print(f"Secondary1 messages: {get_messages(SECONDARY_URL_1)}")
print(f"Secondary2 messages: {get_messages(SECONDARY_URL_2)}")

assert response4.status_code == 200
assert elapsed4 < 1
assert get_messages(MASTER_URL) == ["Msg1", "Msg2", "Msg3", "Msg4"]


response3 = msg3_future.result()
elapsed3 = time.perf_counter() - start3
print(f"Message 3 took {elapsed3:.3f} seconds")
print(f"Master messages: {get_messages(MASTER_URL)}")
print(f"Secondary1 messages: {get_messages(SECONDARY_URL_1)}")
print(f"Secondary2 messages: {get_messages(SECONDARY_URL_2)}")

assert response3.status_code == 200
assert elapsed3 >= 5
assert get_messages(MASTER_URL) == ["Msg1", "Msg2", "Msg3", "Msg4"]
assert get_messages(SECONDARY_URL_1) == ["Msg1", "Msg2", "Msg3", "Msg4"]
assert get_messages(SECONDARY_URL_2)[:3] == ["Msg1", "Msg2", "Msg3"]



print("------Eventual consistency (10s wait)------")
time.sleep(10)
print(f"Master messages: {get_messages(MASTER_URL)}")
print(f"Secondary1 messages: {get_messages(SECONDARY_URL_1)}")
print(f"Secondary2 messages: {get_messages(SECONDARY_URL_2)}")

assert get_messages(MASTER_URL) == ["Msg1", "Msg2", "Msg3", "Msg4"]
assert get_messages(SECONDARY_URL_1) == ["Msg1", "Msg2", "Msg3", "Msg4"]
assert get_messages(SECONDARY_URL_2) == ["Msg1", "Msg2", "Msg3", "Msg4"]

print("--------Iteration 2 Semi-Synchronous replication: All tests passed--------")