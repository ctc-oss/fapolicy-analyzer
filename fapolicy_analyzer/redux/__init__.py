# Copyright 2021 Dr. Carsten Leue
# Copyright Concurrent Technologies Corporation 2021
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
    Implementation of a Redux store with support for adding feature modules, dynamically.
    The store exposes a reactive API based on `RxPY <https://pypi.org/project/Rx/>`_.
"""

# Version of ReduxPy package
__version__ = "0.1.12"

from typing import Tuple

from ._internal.action import create_action, of_type, select_action_payload
from ._internal.epic import combine_epics
from ._internal.feature import (create_feature_module, of_init_feature,
                                select_feature)
from ._internal.reducer import combine_reducers, handle_actions
from ._internal.selectors import select
from ._internal.store import create_store
from ._internal.types import (Action, Epic, Reducer, ReduxFeatureModule,
                              ReduxRootStore, StateType)

__all__: Tuple[str, ...] = (
    "Action",
    "combine_epics",
    "combine_reducers",
    "create_action",
    "create_feature_module",
    "create_store",
    "Epic",
    "handle_actions",
    "of_init_feature",
    "of_type",
    "Reducer",
    "ReduxFeatureModule",
    "ReduxRootStore",
    "select_action_payload",
    "select_feature",
    "select",
    "StateType",
)
