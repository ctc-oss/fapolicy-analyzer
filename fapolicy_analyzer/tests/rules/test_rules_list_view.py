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
from ui.rules.rules_list_view import RulesListView

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture
def widget():
    return RulesListView()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_renders_rules(widget):
    rules = [
        MagicMock(id=1, text="Mock Rule Number 1"),
        MagicMock(id=2, text="Mock Rule Number 2"),
    ]
    widget.render_rules(rules)
    model = widget.get_object("treeView").get_model()
    assert [r.text for r in rules] == [x[0] for x in model]
    assert [r.id for r in rules] == [x[1] for x in model]
    assert ["gainsboro", "white"] == [x[2] for x in model]
