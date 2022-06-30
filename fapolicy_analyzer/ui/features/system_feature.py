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
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence

import gi
from fapolicy_analyzer import System, rollback_fapolicyd
from fapolicy_analyzer.ui.actions import (
    APPLY_CHANGESETS,
    DEPLOY_ANCILLARY_TRUST,
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
    ancillary_trust_deployed,
    clear_changesets,
    error_ancillary_trust,
    error_apply_changesets,
    error_deploying_ancillary_trust,
    error_events,
    error_groups,
    error_rules,
    error_rules_text,
    error_system_trust,
    error_users,
    init_system,
    received_ancillary_trust,
    received_events,
    received_groups,
    received_rules,
    received_rules_text,
    received_system_trust,
    received_users,
    system_initialization_error,
    system_initialized,
)
from fapolicy_analyzer.ui.changeset_wrapper import Changeset
from fapolicy_analyzer.ui.reducers import system_reducer
from fapolicy_analyzer.ui.strings import SYSTEM_INITIALIZATION_ERROR
from fapolicy_analyzer.util.fapd_dbase import fapd_dbase_snapshot
from fapolicy_analyzer.redux import (
    Action,
    ReduxFeatureModule,
    combine_epics,
    create_feature_module,
    of_init_feature,
    of_type,
)
from rx import of, pipe
from rx.operators import catch, ignore_elements, map

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

    def _init_system() -> Action:
        def execute_system():
            try:
                system = System()
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
                dispatch(system_initialized())
            else:
                dispatch(system_initialization_error())

        if system:
            executor = None
            finish(system)
        else:
            executor = ThreadPoolExecutor(max_workers=1)
            executor.submit(execute_system)
        return init_system()

    def _apply_changesets(action: Action) -> Sequence[Changeset]:
        global _system
        changesets = action.payload
        for c in changesets:
            _system = c.apply_to_system(_system)
        return add_changesets(changesets)

    def _get_ancillary_trust(_: Action) -> Action:
        trust = _system.ancillary_trust()
        return received_ancillary_trust(trust)

    def _get_system_trust(_: Action) -> Action:
        trust = _system.system_trust()
        return received_system_trust(trust)

    def _deploy_ancillary_trust(_: Action) -> Action:
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

    def _restore_checkpoint(_: Action) -> Action:
        global _system
        _system = _checkpoint
        rollback_fapolicyd(_system)
        return clear_changesets()

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
        request_ancillary_trust_epic,
        deploy_ancillary_trust_epic,
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
