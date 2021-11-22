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
    'Action',
    'combine_epics',
    'combine_reducers',
    'create_action',
    'create_feature_module',
    'create_store',
    'Epic',
    'handle_actions',
    'of_init_feature',
    'of_type',
    'Reducer',
    'ReduxFeatureModule',
    'ReduxRootStore',
    'select_action_payload',
    'select_feature',
    'select',
    'StateType',
)
