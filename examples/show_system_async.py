from fapolicy_analyzer import *
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

s1 = System()
print("executing system_trust 1")
future_1 = executor.submit(s1.system_trust_async)

s2 = System()
print("executing system_trust 2")
future_2 = executor.submit(s2.system_trust_async)

result_1 = future_1.result()
result_2 = future_2.result()

print(f"found {len(result_1)} system trust entries")
print(f"found {len(result_2)} system trust entries")
