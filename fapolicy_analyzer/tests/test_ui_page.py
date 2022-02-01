# Copyright Concurrent Technologies Corporation 2022
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

import context  # noqa: F401 # isort: skip
from ui.ui_page import UIAction, UIPage


def test_merge_actions():
    action_1 = UIAction(
        name="Action 1",
        tooltip="",
        icon="",
        signals={},
        sensitivity_func=lambda: True,
    )
    action_2 = UIAction(
        name="Action 2",
        tooltip="",
        icon="",
        signals={},
        sensitivity_func=lambda: True,
    )
    other_action = action_1 = UIAction(
        name="Other Action",
        tooltip="",
        icon="",
        signals={},
        sensitivity_func=lambda: True,
    )
    actions_1 = {"actions": [action_1]}
    actions_2 = {"actions": [action_2], "other actions": [other_action]}
    merged_actions = UIPage.merge_actions(actions_1, actions_2)
    assert merged_actions == {
        "actions": [action_1, action_2],
        "other actions": [other_action],
    }
