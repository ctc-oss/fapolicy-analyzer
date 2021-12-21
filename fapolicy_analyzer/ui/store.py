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

from fapolicy_analyzer import System
from redux import Action, create_store
from redux import select_feature
from rx import operators
from rx.core.typing import Observable
from .features import (
    NOTIFICATIONS_FEATURE,
    SYSTEM_FEATURE,
    create_notification_feature,
    create_system_feature,
)


store = create_store()


def init_store(system: System = None):
    """
    Initializes the Redux store.

    Keyword arguments:
    system -- the fapolicy_analyzer.System object, defaults to None. If not provided,
              a new System object will be initialized.  Used for testing purposes only.
    """
    store.add_feature_module(create_notification_feature())
    store.add_feature_module(create_system_feature(store.dispatch, system))


def dispatch(action: Action) -> None:
    store.dispatch(action)


def get_notifications_feature() -> Observable:
    return store.as_observable().pipe(
        operators.map(select_feature(NOTIFICATIONS_FEATURE))
    )


def get_system_feature() -> Observable:
    return store.as_observable().pipe(operators.map(select_feature(SYSTEM_FEATURE)))
