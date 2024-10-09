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

import re
import sys
from inspect import currentframe


def f(formatString):
    frame = currentframe().f_back

    if formatString:
        if sys.version_info < (3, 13):
            formatString = eval(f'f"""{formatString}"""', frame.f_locals,
                                frame.f_globals)
        else:
            formatString = eval(f'f"""{formatString}"""',
                                locals=frame.f_locals,
                                globals=frame.f_globals)
    return formatString


def snake_to_camelcase(string):
    return (
        string[:1].lower()
        + re.sub(
            r"[\-_\.\s]([a-z])", lambda matched: matched.group(1).upper(), string[1:]
        )
        if string
        else string
    )
