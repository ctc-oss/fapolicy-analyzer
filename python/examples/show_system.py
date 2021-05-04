from fapolicy_analyzer import *
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

s1 = System()
print("executing 1")
future_1 = executor.submit(s1.system_trust_allow_threads)

s2 = System()
print("executing 2")
future_2 = executor.submit(s2.system_trust_allow_threads)

result_1 = future_1.result()
result_2 = future_2.result()


print(f"found {len(result_1)} system trust entries")
print(f"found {len(result_2)} system trust entries")

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml

# for t in s1.system_trust():
#     print(f"{t.path} {t.size} {t.hash}")
