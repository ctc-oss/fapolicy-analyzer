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

#
# There are two ways to control a service using the dbus backend components
#

# 1. Stateful object that takes a unit name
d = Handle("fapolicyd")
print(f"==== fapolicyd is {'active' if d.is_active() else 'inactive'} ====")
d.stop()
d.wait_until_inactive()
assert not d.is_active()
d.start()
d.wait_until_active()
assert d.is_active()

# 2. Static calls that use the default "fapolicyd" service
assert is_fapolicyd_active()
stop_fapolicyd()
d.wait_until_inactive()
assert not is_fapolicyd_active()
start_fapolicyd()
d.wait_until_active()
assert is_fapolicyd_active()
