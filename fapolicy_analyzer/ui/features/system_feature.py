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
import logging
import sys

import gi

gi.require_version("Gtk", "3.0")

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence

from fapolicy_analyzer import Changeset, System, rollback_fapolicyd
from fapolicy_analyzer.ui.actions import (
    APPLY_CHANGESETS,
    DEPLOY_ANCILLARY_TRUST,
    REQUEST_ANCILLARY_TRUST,
    REQUEST_EVENTS,
    REQUEST_GROUPS,
    REQUEST_SYSTEM_TRUST,
    REQUEST_USERS,
    RESTORE_SYSTEM_CHECKPOINT,
    SET_SYSTEM_CHECKPOINT,
    add_changesets,
    ancillary_trust_deployed,
    clear_changesets,
    error_ancillary_trust,
    error_deploying_ancillary_trust,
    error_events,
    error_groups,
    error_system_trust,
    error_users,
    init_system,
    received_ancillary_trust,
    received_events,
    received_groups,
    received_system_trust,
    received_users,
    system_initialized,
)
from fapolicy_analyzer.ui.reducers import system_reducer
from fapolicy_analyzer.ui.strings import SYSTEM_INITIALIZATION_ERROR
from fapolicy_analyzer.util.fapd_dbase import fapd_dbase_snapshot
from gi.repository import GLib
from redux import (
    Action,
    ReduxFeatureModule,
    combine_epics,
    create_feature_module,
    of_init_feature,
    of_type,
)
from rx import of, pipe
from rx.operators import catch, ignore_elements, map

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

    def _init_system() -> Action:
        def execute_system():
            try:
                system = System()
                GLib.idle_add(finish, system)
            except RuntimeError:
                logging.exception(SYSTEM_INITIALIZATION_ERROR)
                GLib.idle_add(sys.exit, 1)

        def finish(system: System):
            global _system, _checkpoint
            _system = system
            _checkpoint = _system
            if executor:
                executor.shutdown(cancel_futures=True)
            dispatch(system_initialized())

        if system:
            executor = None
            finish(system)
        else:
            executor = ThreadPoolExecutor(max_workers=1)
            executor.submit(execute_system)
        return init_system()

    def _apply_changesets(changesets: Sequence[Changeset]) -> Sequence[Changeset]:
        global _system
        for c in changesets:
            _system = _system.apply_changeset(c)
        return changesets

    def _get_ancillary_trust(action: Action) -> Action:
        trust = _system.ancillary_trust()
        return received_ancillary_trust(trust)

    def _get_system_trust(action: Action) -> Action:
        trust = _system.system_trust()
        return received_system_trust(trust)

    def _deploy_ancillary_trust(action: Action) -> Action:
        if not fapd_dbase_snapshot():
            logging.warning(
                "Fapolicyd pre-deploy backup failed, continuing with deployment."
            )
        _system.deploy()
        return ancillary_trust_deployed()

    def _set_checkpoint(action: Action) -> Action:
        global _checkpoint
        _checkpoint = _system
        return action

    def _restore_checkpoint(action: Action) -> Action:
        global _system
        _system = _checkpoint
        rollback_fapolicyd(_system)
        return clear_changesets()

    def _get_events(action: Action) -> Action:
        events = _system.events(action.payload)
        return received_events(events)

    def _get_users(action: Action) -> Action:
        users = _system.users()
        return received_users(users)

    def _get_groups(action: Action) -> Action:
        groups = _system.groups()
        return received_groups(groups)

    init_epic = pipe(
        of_init_feature(SYSTEM_FEATURE),
        map(lambda _: _init_system()),
    )

    apply_changesets_epic = pipe(
        of_type(APPLY_CHANGESETS),
        map(lambda action: add_changesets(_apply_changesets(action.payload))),
    )

    request_ancillary_trust_epic = pipe(
        of_type(REQUEST_ANCILLARY_TRUST),
        map(_get_ancillary_trust),
        catch(lambda ex, source: of(error_ancillary_trust(str(ex)))),
    )

    request_system_trust_epic = pipe(
        of_type(REQUEST_SYSTEM_TRUST),
        map(_get_system_trust),
        catch(lambda ex, source: of(error_system_trust(str(ex)))),
    )

    deploy_ancillary_trust_epic = pipe(
        of_type(DEPLOY_ANCILLARY_TRUST),
        map(_deploy_ancillary_trust),
        catch(lambda ex, source: of(error_deploying_ancillary_trust(str(ex)))),
    )

    set_system_checkpoint_epic = pipe(
        of_type(SET_SYSTEM_CHECKPOINT), map(_set_checkpoint), ignore_elements()
    )

    restore_system_checkpoint_epic = pipe(
        of_type(RESTORE_SYSTEM_CHECKPOINT),
        map(_restore_checkpoint),
        catch(lambda ex, source: of(error_deploying_ancillary_trust(str(ex)))),
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

    request_group_epic = pipe(
        of_type(REQUEST_GROUPS),
        map(_get_groups),
        catch(lambda ex, source: of(error_groups(str(ex)))),
    )

    system_epic = combine_epics(
        init_epic,
        apply_changesets_epic,
        request_ancillary_trust_epic,
        deploy_ancillary_trust_epic,
        request_events_epic,
        request_group_epic,
        request_system_trust_epic,
        request_users_epic,
        restore_system_checkpoint_epic,
        set_system_checkpoint_epic,
    )

    return create_feature_module(SYSTEM_FEATURE, system_reducer, epic=system_epic)
