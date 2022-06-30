# Copyright 2021 Dr. Carsten Leue
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
