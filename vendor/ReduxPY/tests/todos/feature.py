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
""" Exposes the feature creator """
from redux import ReduxFeatureModule, create_feature_module, select, select_feature

from .constants import FEATURE_NAME
from .reducer import todo_reducer

select_todos_feature = select_feature(FEATURE_NAME)


def create_todos_feature() -> ReduxFeatureModule:
    """Creates a new feature module

    Returns:
        ReduxFeatureModule -- the feature module
    """
    return create_feature_module(FEATURE_NAME, todo_reducer)
