# Copyright Concurrent Technologies Corporation 2021
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

from fapolicy_analyzer.tests.helpers import refresh_gui
from fapolicy_analyzer.ui.ancillary_trust_file_list import AncillaryTrustFileList
from fapolicy_analyzer.ui.changeset_wrapper import TrustChangeset
from fapolicy_analyzer.ui.configs import Colors
from fapolicy_analyzer.ui.strings import (
    CHANGESET_ACTION_ADD,
    CHANGESET_ACTION_DEL,
    FILE_LIST_CHANGES_HEADER,
)

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip

_trust = [
    MagicMock(status="d", path="/tmp/1", actual=MagicMock(last_modified=123456789)),
    MagicMock(status="t", path="/tmp/2", actual=MagicMock(last_modified=123456789)),
    MagicMock(status="u", path="/tmp/3", actual=MagicMock(last_modified=123456789)),
]


def _get_column(widget, colName):
    return next(
        iter(
            [
                c
                for c in widget.get_object("treeView").get_columns()
                if c.get_title() == FILE_LIST_CHANGES_HEADER
            ]
        )
    )


@pytest.fixture
def widget():
    widget = AncillaryTrustFileList(trust_func=MagicMock())
    return widget


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_uses_custom_trust_func():
    trust_func = MagicMock()
    AncillaryTrustFileList(trust_func=trust_func)
    trust_func.assert_called()


def test_uses_custom_markup_func():
    widget = AncillaryTrustFileList(trust_func=MagicMock())
    widget.init_list(len(_trust))
    widget.append_trust(_trust)
    refresh_gui(delay=0.5)
    view = widget.get_object("treeView")
    assert ["T / <b><u>D</u></b>", "<b><u>T</u></b> / D", "T / D"] == [
        x[0] for x in view.get_model()
    ]
    assert [Colors.LIGHT_RED, Colors.LIGHT_GREEN, Colors.ORANGE] == [
        x[4] for x in view.get_model()
    ]
    assert [Colors.WHITE, Colors.BLACK, Colors.BLACK] == [
        x[5] for x in view.get_model()
    ]


def test_fires_files_added(widget, mocker):
    mockHandler = MagicMock()
    widget.files_added += mockHandler
    widget.on_addBtn_files_added(["foo"])
    mockHandler.assert_called_with(["foo"])


def test_hides_changes_column(widget):
    changesColumn = _get_column(widget, FILE_LIST_CHANGES_HEADER)
    widget.init_list(len(_trust))
    widget.append_trust(_trust)
    assert not changesColumn.get_visible()


def test_shows_changes_column(widget):
    mockChangeset = MagicMock(
        spec=TrustChangeset, serialize=MagicMock(return_value=({"/tmp/foo": "Add"}))
    )
    widget.set_changesets([mockChangeset])
    widget.init_list(len(_trust))
    widget.append_trust(_trust)
    changesColumn = _get_column(widget, FILE_LIST_CHANGES_HEADER)
    assert changesColumn.get_visible()


def test_trust_add_actions_in_view(widget):
    mockChangeset = MagicMock(
        spec=TrustChangeset, serialize=MagicMock(return_value=({"/tmp/1": "Add"}))
    )
    widget.set_changesets([mockChangeset])
    widget.init_list(len(_trust))
    widget.append_trust(_trust)
    refresh_gui(delay=0.5)
    model = widget.get_object("treeView").get_model()
    row = next(iter([x for x in model if x[2] == "/tmp/1"]))
    assert CHANGESET_ACTION_ADD == row[6]


def test_trust_delete_actions_in_view(widget):
    mockChangeset = MagicMock(
        spec=TrustChangeset, serialize=MagicMock(return_value=({"/tmp/foz": "Del"}))
    )
    widget.set_changesets([mockChangeset])
    widget.init_list(len(_trust))
    widget.append_trust(_trust)
    model = widget.get_object("treeView").get_model()
    row = next(iter([x for x in model if x[2] == "/tmp/foz"]))
    assert CHANGESET_ACTION_DEL == row[6]
