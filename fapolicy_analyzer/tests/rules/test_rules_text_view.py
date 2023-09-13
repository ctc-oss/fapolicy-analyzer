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

from unittest.mock import call

import gi
import pytest
from fapolicy_analyzer.ui.rules.rules_text_view import RulesTextView

import context  # noqa: F401 # isort: skip


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture
def widget():
    return RulesTextView()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.ScrolledWindow


def test_renders_rules(widget):
    widget.render_text("foo/")

    textView = widget.get_object("textView")
    textBuffer = textView.get_buffer()
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo/"
    )


def test_handles_bad_language_file(mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.editable_text_view.resources.path",
        return_value="bad path",
    )
    mock_logger = mocker.patch("fapolicy_analyzer.ui.editable_text_view.logging")
    widget = RulesTextView()
    assert widget is not None
    mock_logger.warning.assert_has_calls(
        [
            call("Could not load the rules language file"),
            call("Could not load the rules style file"),
        ]
    )
