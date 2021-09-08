import logging
import sys
from fapolicy_analyzer import Changeset, System
from fapolicy_analyzer.util.fapd_dbase import fapd_dbase_snapshot
from redux import Action, combine_epics, of_type
from rx.operators import catch, ignore_elements, map
from rx import pipe, of
from typing import Sequence
from .actions import (
    DEPLOY_ANCILLARY_TRUST,
    REQUEST_EVENTS,
    REQUEST_GROUPS,
    REQUEST_SYSTEM_TRUST,
    REQUEST_USERS,
    RESTORE_SYSTEM_CHECKPOINT,
    SET_SYSTEM_CHECKPOINT,
    add_changesets,
    APPLY_CHANGESETS,
    clear_changesets,
    error_ancillary_trust,
    REQUEST_ANCILLARY_TRUST,
    error_deploying_ancillary_trust,
    error_events,
    error_groups,
    error_system_trust,
    error_users,
    received_ancillary_trust,
    ancillary_trust_deployed,
    received_events,
    received_groups,
    received_system_trust,
    received_users,
)
from .strings import SYSTEM_INITIALIZATION_ERROR

_system: System
_checkpoint: System


def init_system(system: System = None):
    global _system
    global _checkpoint
    try:
        _system = system or System()
        _checkpoint = _system
    except RuntimeError:
        logging.exception(SYSTEM_INITIALIZATION_ERROR)
        sys.exit(1)


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
    global _system
    _checkpoint = _system
    return action


def _restore_checkpoint(action: Action) -> Action:
    global _system
    global _checkpoint
    _system = _checkpoint
    return clear_changesets()


def _get_events(action: Action) -> Action:
    global _system
    events = _system.events_from(action.payload)
    return received_events(events)


def _get_users(action: Action) -> Action:
    global _system
    users = _system.users()
    return received_users(users)


def _get_groups(action: Action) -> Action:
    global _system
    groups = _system.groups()
    return received_groups(groups)


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
    of_type(RESTORE_SYSTEM_CHECKPOINT), map(_restore_checkpoint)
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
