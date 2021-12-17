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

from fapolicy_analyzer.ui.actions import SYSTEM_INITIALIZED
from redux import Reducer, combine_reducers, handle_actions
from .ancillary_trust_reducer import ancillary_trust_reducer
from .changeset_reducer import changeset_reducer
from .event_reducer import event_reducer
from .group_reducer import group_reducer
from .system_trust_reducer import system_trust_reducer
from .user_reducer import user_reducer


system_initialized_reducer: Reducer = handle_actions(
    {SYSTEM_INITIALIZED: lambda *_: True}, False
)

system_reducer: Reducer = combine_reducers(
    {
        "initialized": system_initialized_reducer,
        "ancillary_trust": ancillary_trust_reducer,
        "changesets": changeset_reducer,
        "events": event_reducer,
        "groups": group_reducer,
        "system_trust": system_trust_reducer,
        "users": user_reducer,
    }
)
