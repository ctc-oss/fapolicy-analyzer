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
import re
from inspect import currentframe


def f(formatString):
    frame = currentframe().f_back
    return (
        eval(f'f"""{formatString}"""', frame.f_locals, frame.f_globals)
        if formatString
        else formatString
    )


def snake_to_camelcase(string):
    return (
        string[:1].lower()
        + re.sub(
            r"[\-_\.\s]([a-z])", lambda matched: matched.group(1).upper(), string[1:]
        )
        if string
        else string
    )
