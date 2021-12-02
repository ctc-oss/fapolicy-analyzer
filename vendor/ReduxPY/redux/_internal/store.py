"""
    Basic implementation of the store
"""

from logging import getLogger
from typing import Iterable, Mapping, MutableMapping, Optional, cast

import rx.operators as op
from rx import Observable, merge
from rx.subject import BehaviorSubject, Subject

from .action import create_action
from .constants import INIT_ACTION
from .epic import normalize_epic, run_epic
from .reducer import combine_reducers
from .types import (Action, Epic, Reducer, ReduxFeatureModule, ReduxRootState,
                    ReduxRootStore, StateType)

logger = getLogger(__name__)


def select_id(module: ReduxFeatureModule) -> str:
    """ Selects the ID from a module

        Args:
            module: the module

        Returns:
            The module identifier
    """
    return module.id


def select_dependencies(
        module: ReduxFeatureModule) -> Iterable[ReduxFeatureModule]:
    """ Selects the dependencies from a module

        Args:
            module: the module

        Returns:
            The module dependencies
    """
    return module.dependencies


def select_reducer(module: ReduxFeatureModule) -> Optional[Reducer]:
    """ Selects the reducer from a module

        Args:
            module: the module

        Returns:
            The module reducer
    """
    return module.reducer


def select_epic(module: ReduxFeatureModule) -> Optional[Epic]:
    """ Selects the epic from a module

        Args:
            module: the module

        Returns:
            The module epic
    """
    return module.epic


def has_reducer(module: ReduxFeatureModule) -> bool:
    """ Tests if a module defines a reducer

        Args:
            module: the module

        Returns:
            True if the module has a reducer, else False

    """
    return bool(select_reducer(module))


def identity_reducer(state: StateType, _: Action) -> StateType:
    """ Reducer function that returns the original state
    """
    return state


def reduce_reducers(
    dst: Mapping[str, Reducer], module: ReduxFeatureModule
) -> Mapping[str, Reducer]:
    """ Reduces the reducer on a module into a dictionary

        Args:
            dst: the target dictionary
            module: the module to reduce

        Returns:
            the reduced dictionary

    """
    reducer: Optional[Reducer] = select_reducer(module)
    return cast(Mapping[str, Reducer], {
                **dst, select_id(module): reducer}) if reducer else dst


def create_store(initial_state: Optional[ReduxRootState] = None) -> ReduxRootStore:  # pylint: disable=too-many-locals
    """ Constructs a new store that can handle feature modules.

        Args:
            initial_state: optional initial state of the store, will typically be the empty dict

        Returns:
            An implementation of the store
    """

    # current reducer
    reducer: Reducer = identity_reducer

    def replace_reducer(new_reducer: Reducer) -> None:
        """ Callback that replaces the current reducer

            Args:
                new_reducer: the new reducer

        """
        nonlocal reducer
        reducer = new_reducer

    # subject used to dispatch actions
    actions = Subject()

    # the shared action observable
    actions_ = actions.pipe(op.share())

    _dispatch = actions.on_next

    # our current state
    state = BehaviorSubject(initial_state if initial_state else {})

    # shutdown trigger
    done_ = Subject()

    # The set of known modules, to avoid cycles and duplicate registration
    modules: MutableMapping[str, ReduxFeatureModule] = {}

    # Sequence of added modules
    module_subject = Subject()

    # Subscribe to the resolved modules
    module_ = module_subject.pipe(op.distinct(select_id), op.share())

    # Build the reducers
    reducer_ = module_.pipe(
        op.filter(has_reducer),
        op.scan(reduce_reducers, {}),
        op.map(combine_reducers),
        op.map(replace_reducer),
    )

    # Build the epic
    epic_ = module_.pipe(
        op.map(select_epic),
        op.filter(bool),
        op.map(normalize_epic)
    )

    # Root epic that combines all of the incoming epics
    def root_epic(
        action_: Observable, state_: Observable
    ) -> Observable:
        """ Implementation of the root epic. If listens for new epics
            to come in and automatically subscribes.

            Args:
                action_: the action observable
                state_: the state observable

            Returns
                The observable of resulting actions
        """
        return epic_.pipe(
            op.flat_map(run_epic(action_, state_)),
            op.map(_dispatch)
        )

    # notifications about new feature states
    new_module_ = module_.pipe(
        op.map(select_id),
        op.map(create_action(INIT_ACTION)),
        op.map(_dispatch),
    )

    def _add_feature_module(module: ReduxFeatureModule):
        """ Registers a new feature module

            Args:
                module: the new feature module

        """
        module_id = select_id(module)
        if not module_id in modules:
            modules[module_id] = module
            for dep in select_dependencies(module):
                _add_feature_module(dep)
            module_subject.on_next(module)

    # all state
    internal_ = merge(root_epic(actions_, state), reducer_, new_module_).pipe(
        op.ignore_elements()
    )

    def _as_observable() -> Observable:
        """ Returns the state as an observable

            Returns:
                the observable
        """
        return state

    def _on_completed() -> None:
        """ Triggers the done event """
        done_.on_next(None)

    merge(actions_, internal_).pipe(
        op.map(lambda action: reducer(state.value, action)),
        op.take_until(done_),
    ).subscribe(state, logger.error)

    return ReduxRootStore(
        _as_observable, _dispatch, _add_feature_module, _dispatch, _on_completed
    )
