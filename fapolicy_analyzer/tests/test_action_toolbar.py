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

from unittest.mock import MagicMock

import gi
import pytest
from fapolicy_analyzer.ui.action_toolbar import ActionToolbar
from fapolicy_analyzer.ui.ui_page import UIAction

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip

_test_actions = {
    "actions": [
        UIAction(
            name="Test Action",
            tooltip="Test Action Tooltip",
            icon="window-close",
            signals={},
            sensitivity_func=lambda: True,
        )
    ],
}


@pytest.fixture
def widget():
    return ActionToolbar(_test_actions)


def test_creates_widget(widget):
    assert isinstance(widget, Gtk.Toolbar)


def test_adds_action_buttons(widget):
    actions = [a for acts in _test_actions.values() for a in acts]
    assert widget.get_n_items() == len(actions)
    for idx, action in enumerate(actions):
        button = widget.get_nth_item(idx)
        assert button.get_label() == action.name
        assert button.get_tooltip_text() == action.tooltip
        assert (
            button.get_icon_widget().get_pixbuf()
            == Gtk.IconTheme.get_default().load_icon(
                action.icon, Gtk.IconSize.LARGE_TOOLBAR, 0
            )
        )
        assert button.get_sensitive() == action.sensitivity_func()


def test_adds_new_action_button(widget):
    new_action = UIAction(
        name="New Action",
        tooltip="New Action Tooltip",
        icon="folder-new",
        signals={},
        sensitivity_func=lambda: True,
    )
    new_actions = {"actions": [*_test_actions["actions"], new_action]}
    widget.rebuild_toolbar(new_actions)
    assert widget.get_n_items() == len(
        [a for acts in new_actions.values() for a in acts]
    )


def test_uses_fallback_missing_image():
    actions = {
        "actions": [
            UIAction(
                name="Test Action",
                tooltip="Test Action Tooltip",
                icon="bad icon name",
                signals={},
                sensitivity_func=lambda: True,
            )
        ]
    }
    widget = ActionToolbar(actions)
    button = widget.get_nth_item(0)
    assert (
        button.get_icon_widget().get_pixbuf()
        == Gtk.IconTheme.get_default().load_icon(
            "image-missing", Gtk.IconSize.LARGE_TOOLBAR, 0
        )
    )


def test_handles_failed_icon_load(mocker):
    mock_theme = MagicMock(load_icon=MagicMock(side_effect=Exception()))
    mocker.patch(
        "gi.repository.Gtk.IconTheme.get_default",
        return_value=mock_theme,
    )
    widget = ActionToolbar(_test_actions)
    button = widget.get_nth_item(0)
    assert button.get_icon_widget() is None


def test_adds_seperators(widget):
    new_action = UIAction(
        name="New Action",
        tooltip="New Action Tooltip",
        icon="folder-new",
        signals={},
        sensitivity_func=lambda: True,
    )
    new_actions = {**_test_actions, "New Actions": [new_action]}
    widget.rebuild_toolbar(new_actions)
    assert isinstance(widget.get_nth_item(1), Gtk.SeparatorToolItem)


def test_refresh_buttons_sensitivity():
    sensitive = True
    action = UIAction(
        name="Action",
        tooltip="Action Tooltip",
        icon="folder-new",
        signals={},
        sensitivity_func=lambda: sensitive,
    )
    widget = ActionToolbar({"": [action]})
    assert widget.get_nth_item(0).get_sensitive() == sensitive
    sensitive = False
    widget.refresh_buttons_sensitivity()
    assert widget.get_nth_item(0).get_sensitive() == sensitive


def test_wires_up_signal():
    mock_clicked_handler = MagicMock()
    action = UIAction(
        name="Action",
        tooltip="Action Tooltip",
        icon="folder-new",
        signals={"clicked": mock_clicked_handler},
        sensitivity_func=lambda: True,
    )
    widget = ActionToolbar({"": [action]})
    widget.get_nth_item(0).get_child().clicked()
    mock_clicked_handler.assert_called_once()
