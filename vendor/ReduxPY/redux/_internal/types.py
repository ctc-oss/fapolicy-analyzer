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
"""
    Module doc
"""
from typing import (Any, Callable, Iterable, Mapping, NamedTuple, Optional,
                    TypeVar)

from rx import Observable
from rx.core.typing import OnCompleted

StateType = TypeVar("StateType")

PayloadType = TypeVar("PayloadType")

ReduxRootState = Mapping[str, StateType]


class Action(NamedTuple):
    """ Action implementation that takes a payload """

    type: str
    """Identifier for the action, must be globally unique."""

    payload: Any
    """The action action payload"""


Epic = Callable[[Observable, Observable], Observable]

Reducer = Callable[[StateType, Action], StateType]


class ReduxFeatureModule(NamedTuple):
    """ Defines the feature module. The ID identifies the section in the state and
        is also used to globally discriminate features.

        After instantiating a feature store the store will fire an initialization action
        for that feature. Use :py:meth:`~redux.of_init_feature` to
        register for these initialization actions.
    """

    id: str
    """Identifier of the module, will also be used as a namespace into the state."""

    reducer: Optional[Reducer]
    """Reducer that handles module specific actions."""

    epic: Optional[Epic]
    """Epic that handles module specific asynchronous operations."""

    dependencies: Iterable['ReduxFeatureModule']
    """Dependencies on other feature modules"""


class ReduxRootStore(NamedTuple):
    """ Implementation of a store that manages sub-state as features. Features are added
        to the store automatically, when required by the select method.
    """

    as_observable: Callable[[], Observable]
    """Converts the store to an observable of state emissions"""

    dispatch: Callable[[Action], None]
    """Dispatches a single action to the store"""

    add_feature_module: Callable[[ReduxFeatureModule], None]
    """ Adds a new feature module """

    on_next: Callable[[Action], None]
    """ Alias for :py:meth:`~redux.ReduxRootStore.dispatch` """

    on_completed: OnCompleted
    """ Shuts down the store """
