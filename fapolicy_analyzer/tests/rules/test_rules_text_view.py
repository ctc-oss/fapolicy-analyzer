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
from unittest.mock import mock_open, patch

import gi
import pytest
from callee import Attrs, InstanceOf
from redux import Action
from ui.actions import ADD_NOTIFICATION
from ui.rules.rules_text_view import RulesTextView
from ui.strings import RULES_FILE_READ_ERROR

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture
def widget():
    return RulesTextView()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.ScrolledWindow


def test_renders_rules(widget):
    expected = "Mock Rule Number 1\nMock Rule Number 2"
    with patch(
        "ui.rules.rules_text_view.open", mock_open(read_data=expected), create=True
    ) as m:
        widget.render_rules("foo/")

    m.assert_called_with("foo/", "r")
    textView = widget.get_object("textView")
    textBuffer = textView.get_buffer()
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == expected
    )


def test_renders_rules_with_exception(widget, mocker):
    mock_dispatch = mocker.patch("ui.rules.rules_text_view.dispatch")
    with patch(
        "ui.rules.rules_text_view.open", mock_open(read_data=""), create=True
    ) as m:
        m.side_effect = IOError()
        widget.render_rules("foo/")

    m.assert_called_with("foo/", "r")
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(text=RULES_FILE_READ_ERROR),
        )
    )
