# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
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
