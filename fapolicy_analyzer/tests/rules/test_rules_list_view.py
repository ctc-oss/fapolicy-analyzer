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
from ui.configs import Colors
from ui.rules.rules_list_view import RulesListView

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip

mock_rules = [
    MagicMock(
        id=1,
        text="Mock Rule Number 1",
        is_valid=True,
        origin="Rule File 1",
        info=[],
    ),
    MagicMock(
        id=2,
        text="Mock Rule Number 2",
        origin="Rule File 1",
        is_valid=True,
        info=[MagicMock(category="i", message="info message")],
    ),
    MagicMock(
        id=3,
        text="Mock Rule Number 3",
        origin="Rule File 2",
        is_valid=True,
        info=[
            MagicMock(category="w", message="warning message"),
            MagicMock(category="i", message="other info"),
        ],
    ),
    MagicMock(
        id=4,
        text="Mock Rule Number 4",
        origin="Rule File 2",
        is_valid=False,
        info=[
            MagicMock(category="w", message="warning message"),
            MagicMock(category="i", message="other info"),
        ],
    ),
]


@pytest.fixture
def widget():
    return RulesListView()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_renders_origin_files(widget):
    def get_origin_rows(store, treepath, treeiter):
        nonlocal origins
        if treepath.get_depth() == 1:
            origins += [store[treeiter]]

    widget.render_rules(mock_rules)
    model = widget.get_object("treeView").get_model()
    origins = []

    model.foreach(get_origin_rows)
    assert sorted(set([f"[{r.origin}]" for r in mock_rules])) == [x[0] for x in origins]
    assert set([-1]) == set([x[1] for x in origins])
    assert set([Colors.DARK_GRAY]) == set([x[2] for x in origins])
    assert set([Colors.WHITE]) == set([x[3] for x in origins])


def test_renders_rules(widget):
    def get_rule_rows(store, treepath, treeiter):
        nonlocal rules
        if treepath.get_depth() == 2:
            rules += [store[treeiter]]

    widget.render_rules(mock_rules)
    model = widget.get_object("treeView").get_model()
    rules = []

    model.foreach(get_rule_rows)
    assert [r.text for r in mock_rules] == [x[0] for x in rules]
    assert [r.id for r in mock_rules] == [x[1] for x in rules]
    assert [Colors.WHITE, Colors.SHADED, Colors.WHITE, Colors.SHADED] == [
        x[2] for x in rules
    ]
    assert [Colors.BLACK, Colors.BLUE, Colors.ORANGE, Colors.RED] == [
        x[3] for x in rules
    ]


def test_renders_info_rows(widget):
    expected_messages = ["[w] warning message", "[i] other info"]
    expected_colors = [Colors.ORANGE, Colors.BLUE]

    widget.render_rules([mock_rules[3]])
    model = widget.get_object("treeView").get_model()
    info_messages = []
    info_colors = []

    def get_assertion_info(store, treepath, treeiter):
        nonlocal info_messages, info_colors
        if treepath.get_depth() > 2:
            info_messages.append(store[treeiter][0])
            info_colors.append(store[treeiter][3])

    model.foreach(get_assertion_info)
    assert info_messages == expected_messages
    assert info_colors == expected_colors
