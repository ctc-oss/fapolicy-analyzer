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

from unittest.mock import MagicMock

import gi
import pytest
from fapolicy_analyzer.ui.configs import Colors, FontWeights
from fapolicy_analyzer.ui.rules.rules_status_info import RulesStatusInfo

import context  # noqa: F401 # isort: skip

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture
def widget():
    return RulesStatusInfo()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Frame


def test_renders_status_info(widget):
    mock_rules = [
        MagicMock(
            id=1,
            text="Mock Rule Number 1",
            is_valid=True,
            info=[MagicMock(category="e", message="error message")],
        ),
        MagicMock(
            id=2,
            text="Mock Rule Number 2",
            is_valid=False,
            info=[
                MagicMock(category="w", message="warning message"),
                MagicMock(category="i", message="info message"),
            ],
        ),
    ]
    widget.render_rule_status(mock_rules)
    model = widget.get_object("statusList").get_model()

    expected = [
        (1, "1 invalid rule(s) found"),
        (2, "rule 1: error message"),
        (1, "1 warning(s) found"),
        (2, "rule 2: warning message"),
        (1, "1 informational message(s)"),
        (2, "rule 2: info message"),
    ]
    actual = []

    def get_rows(store, treepath, treeiter):
        actual.append((treepath.get_depth(), store[treeiter][0]))

    model.foreach(get_rows)
    assert actual == expected


@pytest.mark.parametrize(
    "category, color, weight, index",
    [
        ("e", Colors.RED, FontWeights.BOLD, 0),
        ("w", Colors.ORANGE, FontWeights.BOLD, 1),
        ("i", Colors.BLUE, FontWeights.BOLD, 2),
    ],
)
def test_renders_message_style(widget, category, color, weight, index):
    mock_rules = [
        MagicMock(
            id=1,
            text="Mock Rule Number 1",
            is_valid=True,
            info=[MagicMock(category=category, message="message")],
        ),
    ]
    widget.render_rule_status(mock_rules)
    model = widget.get_object("statusList").get_model()

    assert model[index][-2:] == [color, weight]
