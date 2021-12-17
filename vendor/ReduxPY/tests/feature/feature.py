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
from typing import Any
from rx import Observable, pipe
from rx.operators import do_action, filter, map, ignore_elements

from redux import (
    Epic,
    Reducer,
    ReduxFeatureModule,
    combine_epics,
    create_action,
    create_feature_module,
    handle_actions,
    of_init_feature,
    of_type,
    select_action_payload,
    select_feature,
    StateType,
    Action,
)

SAMPLE_FEATURE = "SAMPLE_FEATURE"

ADD_SAMPLE_ACTION = "ADD_SAMPLE_ACTION"

add_sample_action = create_action(ADD_SAMPLE_ACTION)
select_sample_feature_module = select_feature(SAMPLE_FEATURE)


def create_sample_feature() -> ReduxFeatureModule:
    """
        Constructs a new sample feature
    """

    def handle_sample_action(state: Any, action: Action) -> Any:
        return select_action_payload(action)

    sample_reducer = handle_actions({ADD_SAMPLE_ACTION: handle_sample_action})

    add_epic = pipe(of_type(ADD_SAMPLE_ACTION), ignore_elements(),)

    sample_epic = combine_epics(add_epic)

    return create_feature_module(SAMPLE_FEATURE, sample_reducer, sample_epic)
