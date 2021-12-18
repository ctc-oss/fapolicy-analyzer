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

import time

from fapolicy_analyzer import *

#
# There are two ways to control a service using the dbus backend components
#

# 1. Static calls that use the default "fapolicyd" service
print(is_fapolicyd_active())
stop_fapolicyd()
print(is_fapolicyd_active())
start_fapolicyd()
print(is_fapolicyd_active())

# 2. Stateful object that takes a unit name
d = Handle("fapolicyd")
print(d.is_active())
d.stop()
time.sleep(1)
print(d.is_active())
d.start()
print(d.is_active())
