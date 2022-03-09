# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from fapolicy_analyzer import *

green = '\033[91m'
red = '\033[92m'
yellow = '\033[93m'
blue = '\033[96m'

s1 = System()
for r in s1.rules():
    print(red if r.is_valid else green, end='')
    print(f"{r.id} {r.text} \033[0m")
    for info in r.info:
        print(yellow if info.category == 'w' else blue, end='')
        print(f"\t- [{info.category}] {info.message} \033[0m")
