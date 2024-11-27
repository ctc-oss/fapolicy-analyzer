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

from typing import Tuple

from fapolicy_analyzer.ui.reducers.application_reducer import application_reducer
from fapolicy_analyzer.ui.reducers.notification_reducer import notification_reducer
from fapolicy_analyzer.ui.reducers.profiler_reducer import profiler_reducer
from fapolicy_analyzer.ui.reducers.stats_reducer import stats_reducer
from fapolicy_analyzer.ui.reducers.system_reducer import system_reducer

__all__: Tuple[str, ...] = (
    "application_reducer",
    "notification_reducer",
    "profiler_reducer",
    "stats_reducer",
    "system_reducer",
)
