# Copyright Concurrent Technologies Corporation 2023
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

import pytest
from rx.core.typing import Observable

from fapolicy_analyzer.tests.mocks import mock_System
from fapolicy_analyzer.ui.reducers.application_reducer import AppConfigState
from fapolicy_analyzer.ui.store import (
    get_application_feature,
    get_notifications_feature,
    get_system_feature,
    init_store,
)


@pytest.mark.parametrize(
    ["feature_getter", "initial_state_type"],
    [
        (get_notifications_feature, list),
        (get_application_feature, AppConfigState),
        (get_system_feature, dict),
    ],
)
def test_get_features(feature_getter, initial_state_type):
    def on_next(x):
        assert isinstance(x, initial_state_type)

    init_store(mock_System())
    feature = feature_getter()
    assert isinstance(feature, Observable)
    feature.subscribe(on_next=on_next)
