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

from typing import Any
from rx import pipe
from rx.operators import ignore_elements

from fapolicy_analyzer.redux import (
    ReduxFeatureModule,
    combine_epics,
    create_action,
    create_feature_module,
    handle_actions,
    of_type,
    select_action_payload,
    select_feature,
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
