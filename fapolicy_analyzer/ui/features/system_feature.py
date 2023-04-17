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

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Event
from typing import Callable, Dict, Sequence

import gi
from rx import of
from rx.core.pipe import pipe
from rx.operators import catch, filter, map

from fapolicy_analyzer import (
    System,
    Trust,
    check_ancillary_trust,
    check_system_trust,
    rollback_fapolicyd,
    unchecked_system,
)
from fapolicy_analyzer.redux import (
    Action,
    ReduxFeatureModule,
    combine_epics,
    create_feature_module,
    of_init_feature,
    of_type,
)
from fapolicy_analyzer.ui.actions import (
    APPLY_CHANGESETS,
    DEPLOY_SYSTEM,
    REQUEST_ANCILLARY_TRUST,
    REQUEST_EVENTS,
    REQUEST_GROUPS,
    REQUEST_RULES,
    REQUEST_RULES_TEXT,
    REQUEST_SYSTEM_TRUST,
    REQUEST_USERS,
    RESTORE_SYSTEM_CHECKPOINT,
    SET_SYSTEM_CHECKPOINT,
    add_changesets,
    ancillary_trust_load_complete,
    ancillary_trust_load_started,
    error_ancillary_trust,
    error_apply_changesets,
    error_deploying_system,
    error_events,
    error_groups,
    error_rules,
    error_rules_text,
    error_system_trust,
    error_users,
    init_system,
    received_ancillary_trust_update,
    received_events,
    received_groups,
    received_rules,
    received_rules_text,
    received_system_trust_update,
    received_users,
    system_checkpoint_set,
    system_deployed,
    system_initialization_error,
    system_received,
    system_trust_load_complete,
    system_trust_load_started,
)
from fapolicy_analyzer.ui.reducers import system_reducer
from fapolicy_analyzer.ui.strings import SYSTEM_INITIALIZATION_ERROR
from fapolicy_analyzer.util.fapd_dbase import fapd_dbase_snapshot

gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # isort: skip


SYSTEM_FEATURE = "system"
_system: System
_checkpoint: System


def create_system_feature(
    dispatch: Callable, system: System = None
) -> ReduxFeatureModule:
    """
    Creates a Redux feature of type System

    Keyword arguments:
    dispatch -- the Redux Store dispatch method, used for dispatching actions
    system -- the fapolicy_analyzer.System object, defaults to None. If not provided,
              a new System object will be initialized.  Used for testing purposes only.
    """

    system_trust_checks: Dict[System, Event] = {}
    ancillary_trust_checks: Dict[System, Event] = {}

    def _init_system() -> Action:
        def execute_system():
            try:
                system = unchecked_system()
                GLib.idle_add(finish, system)
            except RuntimeError:
                logging.exception(SYSTEM_INITIALIZATION_ERROR)
                GLib.idle_add(finish, None)

        def finish(system: System):
            global _system, _checkpoint
            logging.debug(f"system_feature::finish::system = {type(system)}")
            _system = system
            _checkpoint = _system

            if executor:
                executor.shutdown()

            if system:
                dispatch(system_received(system))
                dispatch(system_checkpoint_set(_checkpoint))
            else:
                dispatch(system_initialization_error(SYSTEM_INITIALIZATION_ERROR))

        if system:
            executor = None
            finish(system)
        else:
            executor = ThreadPoolExecutor(max_workers=1)
            executor.submit(execute_system)
        return init_system()

    def _idle_dispatch(action: Action):
        GLib.idle_add(dispatch, action)

    def _set_system(system: System):
        global _system
        nonlocal ancillary_trust_checks, system_trust_checks

        events = [
            e
            for e in (
                ancillary_trust_checks.pop(system, None),
                system_trust_checks.pop(system, None),
            )
            if e
        ]
        for e in events:
            e.set()

        _system = system

    def _apply_changesets(action: Action) -> Action:
        global _system
        changesets = action.payload

        for c in changesets:
            _system = c.apply_to_system(_system)
            _set_system(_system)

        dispatch(system_received(_system))
        return add_changesets(changesets)

    def _check_disk_trust_update(
        updates: Sequence[Trust],
        count: int,
        action_fn: Callable[[Trust, int, float], Action],
        event: Event,
        timestamp: float,
    ):
        if event.is_set():
            return

        # merge the updated trust into the system
        _system.merge(updates)
        # dispatch the update
        _idle_dispatch(action_fn(updates, count, timestamp))

    def _check_disk_trust_complete(
        action_fn: Callable[[float], Action],
        flag_fn: Callable[[], None],
        event: Event,
        timestamp: float,
    ):
        if not event.is_set():
            _idle_dispatch(action_fn(timestamp))
        flag_fn()

    def _get_ancillary_trust(action: Action) -> Action:
        nonlocal ancillary_trust_checks

        def checking_finished():
            nonlocal ancillary_trust_checks
            ancillary_trust_checks.pop(_system)

        if _system in ancillary_trust_checks:
            return action

        event = Event()
        timestamp = time.time()
        ancillary_trust_checks[_system] = event

        update = partial(
            _check_disk_trust_update,
            action_fn=received_ancillary_trust_update,
            event=event,
            timestamp=timestamp,
        )
        done = partial(
            _check_disk_trust_complete,
            action_fn=ancillary_trust_load_complete,
            flag_fn=checking_finished,
            event=event,
            timestamp=timestamp,
        )
        total_to_check = check_ancillary_trust(_system, update, done)
        return ancillary_trust_load_started(total_to_check, timestamp)

    def _get_system_trust(action: Action) -> Action:
        nonlocal system_trust_checks

        def checking_finished():
            nonlocal system_trust_checks
            system_trust_checks.pop(_system)

        if _system in system_trust_checks:
            return action

        event = Event()
        timestamp = time.time()
        system_trust_checks[_system] = event

        update = partial(
            _check_disk_trust_update,
            action_fn=received_system_trust_update,
            event=event,
            timestamp=timestamp,
        )
        done = partial(
            _check_disk_trust_complete,
            action_fn=system_trust_load_complete,
            flag_fn=checking_finished,
            event=event,
            timestamp=timestamp,
        )
        total_to_check = check_system_trust(_system, update, done)
        return system_trust_load_started(total_to_check, timestamp)

    def _deploy_system(_: Action) -> Action:
        if not fapd_dbase_snapshot():
            logging.warning(
                "Fapolicyd pre-deploy backup failed, continuing with deployment."
            )
        _system.deploy()
        return system_deployed()

    def _set_checkpoint(action: Action) -> Action:
        global _checkpoint
        _checkpoint = _system
        return system_checkpoint_set(_checkpoint)

    def _restore_checkpoint(_: Action) -> Action:
        _set_system(_checkpoint)
        rollback_fapolicyd(_system)
        return system_received(_system)

    def _get_events(action: Action) -> Action:
        log_type, file = action.payload
        if log_type == "debug":
            events = _system.load_debuglog(file)
        elif log_type == "syslog":
            events = _system.load_syslog()
        else:
            events = []
        return received_events(events)

    def _get_users(_: Action) -> Action:
        users = _system.users()
        return received_users(users)

    def _get_groups(_: Action) -> Action:
        groups = _system.groups()
        return received_groups(groups)

    def _get_rules(_: Action) -> Action:
        rules = _system.rules()
        return received_rules(rules)

    def _get_rules_text(_: Action) -> Action:
        text = _system.rules_text()
        return received_rules_text(text)

    init_epic = pipe(
        of_init_feature(SYSTEM_FEATURE),
        map(lambda _: _init_system()),
    )

    apply_changesets_epic = pipe(
        of_type(APPLY_CHANGESETS),
        map(_apply_changesets),
        catch(lambda ex, source: of(error_apply_changesets(str(ex)))),
    )

    request_ancillary_trust_epic = pipe(
        of_type(REQUEST_ANCILLARY_TRUST),
        map(_get_ancillary_trust),
        filter(lambda a: a.type != REQUEST_ANCILLARY_TRUST),
        catch(lambda ex, source: of(error_ancillary_trust(str(ex)))),
    )

    request_system_trust_epic = pipe(
        of_type(REQUEST_SYSTEM_TRUST),
        map(_get_system_trust),
        filter(lambda a: a.type != REQUEST_SYSTEM_TRUST),
        catch(lambda ex, source: of(error_system_trust(str(ex)))),
    )

    deploy_system_epic = pipe(
        of_type(DEPLOY_SYSTEM),
        map(_deploy_system),
        catch(lambda ex, source: of(error_deploying_system(str(ex)))),
    )

    set_system_checkpoint_epic = pipe(
        of_type(SET_SYSTEM_CHECKPOINT), map(_set_checkpoint)
    )

    restore_system_checkpoint_epic = pipe(
        of_type(RESTORE_SYSTEM_CHECKPOINT),
        map(_restore_checkpoint),
        catch(lambda ex, source: of(error_deploying_system(str(ex)))),
    )

    request_events_epic = pipe(
        of_type(REQUEST_EVENTS),
        map(_get_events),
        catch(lambda ex, source: of(error_events(str(ex)))),
    )

    request_users_epic = pipe(
        of_type(REQUEST_USERS),
        map(_get_users),
        catch(lambda ex, source: of(error_users(str(ex)))),
    )

    request_groups_epic = pipe(
        of_type(REQUEST_GROUPS),
        map(_get_groups),
        catch(lambda ex, source: of(error_groups(str(ex)))),
    )

    request_rules_epic = pipe(
        of_type(REQUEST_RULES),
        map(_get_rules),
        catch(lambda ex, source: of(error_rules(str(ex)))),
    )

    request_rules_text_epic = pipe(
        of_type(REQUEST_RULES_TEXT),
        map(_get_rules_text),
        catch(lambda ex, source: of(error_rules_text(str(ex)))),
    )

    system_epic = combine_epics(
        init_epic,
        apply_changesets_epic,
        deploy_system_epic,
        request_ancillary_trust_epic,
        request_events_epic,
        request_groups_epic,
        request_rules_epic,
        request_rules_text_epic,
        request_system_trust_epic,
        request_users_epic,
        restore_system_checkpoint_epic,
        set_system_checkpoint_epic,
    )

    return create_feature_module(SYSTEM_FEATURE, system_reducer, epic=system_epic)
