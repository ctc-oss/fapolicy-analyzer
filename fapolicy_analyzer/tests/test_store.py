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

from importlib import reload

import pytest
from rx.core.typing import Observable

from fapolicy_analyzer.tests.mocks import mock_System
from fapolicy_analyzer.ui import store
from fapolicy_analyzer.ui.reducers.application_reducer import AppConfigState


@pytest.mark.parametrize(
    ["feature_under_test", "initial_state_type"],
    [
        (store.get_notifications_feature, list),
        (store.get_application_feature, AppConfigState),
        (store.get_system_feature, dict),
    ],
)
def test_get_features(feature_under_test, initial_state_type):
    def on_next(x):
        assert isinstance(x, initial_state_type)

    reload(store)
    store.init_store(mock_System())
    feature = feature_under_test()
    assert isinstance(feature, Observable)
    feature.subscribe(on_next=on_next)
