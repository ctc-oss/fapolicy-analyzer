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

# Unknown Decision
print(rule_text_error_check("foo perm=any all : all"))

# Expected one of 'any', 'open', 'execute'
print(rule_text_error_check("allow perm=foo all : all"))

# None (aka, valid)
print(rule_text_error_check("allow perm=any all : all"))
