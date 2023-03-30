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

from unittest.mock import MagicMock, mock_open

from fapolicy_analyzer.redux import ReduxFeatureModule
from fapolicy_analyzer.ui.actions import request_app_config
from fapolicy_analyzer.ui.features.application_feature import create_application_feature
from fapolicy_analyzer.ui.store import dispatch, init_store

test_config = """[ui]
initial_view = 'foo'
"""


def test_creates_application_feature():
    assert isinstance(create_application_feature(), ReduxFeatureModule)


def test_request_app_config_epic(mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.features.application_feature.config_file_path",
        return_value="/tmp",
    )
    _mock_open = mocker.patch("builtins.open", mock_open(read_data=test_config))
    mock_received_app_config = mocker.patch(
        "fapolicy_analyzer.ui.features.application_feature.received_app_config"
    )
    init_store(MagicMock())
    dispatch(request_app_config())
    _mock_open.assert_called_with("/tmp", "r")
    mock_received_app_config.assert_called_with({"initial_view": "foo"})


def test_request_app_config_error(mocker):
    MagicMock(deploy=MagicMock())
    mocker.patch(
        "fapolicy_analyzer.ui.features.application_feature.config_file_path",
        side_effect=Exception("config file path error"),
    )
    mock_error_action = mocker.patch(
        "fapolicy_analyzer.ui.features.application_feature.error_app_config"
    )
    init_store(MagicMock())
    dispatch(request_app_config())
    mock_error_action.assert_called_with("config file path error")
